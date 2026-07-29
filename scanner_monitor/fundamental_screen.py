"""
fundamental_screen.py
=====================
"NO-TRADE" fundamental filter for the swing scanner.

Runs BEFORE the technical scan and excludes structurally broken / governance-risky
companies from the 15%/30-day swing universe. Stocks that fail this gate never
reach the technical backtest — protecting you from the classic "technically
perfect but fundamentally doomed" trap (e.g. a bullish smallcap with 80%
promoter pledge and negative operating cash flow).

Philosophy — it is a NO-TRADE filter, not a stock picker.
  * Missing data = PASS with warning (never fail on absence, unless strict_mode)
  * Financials (banks/NBFCs/HFCs/insurers) skip leverage/interest-cover checks
  * Thresholds are LENIENT — kick out clearly broken, not marginally weak.
  * Governance data yfinance can't provide (promoter pledge, auditor qualification)
    is read from an optional `governance_overrides.csv` supplied by the user.

Data sources (priority order):
  1. governance_overrides.csv  (user-supplied — highest priority)
  2. yfinance .info             (valuation & quality metrics)
  3. yfinance quarterly_income_stmt / income_stmt (growth & interest cover)

Public API:
    load_overrides(path)              -> dict of manual data
    fetch_fundamentals(ticker)        -> raw fields for one stock (cached 24h)
    screen_universe(tickers, secmap, config, cb) -> (results, sector_medians)
    screen_fundamentals(bare, sector, fund, medians, ov, cfg) -> single-stock verdict
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None


# ======================================================================================
#  1. CONFIGURATION — thresholds for the NO-TRADE gate
# ======================================================================================
DEFAULT_FUNDA_CONFIG = {
    # ---- master switches per pillar ----
    "valuation_enabled":   False,   # OFF: momentum swings can carry rich multiples
    "quality_enabled":     True,    # ON:  the real "broken business" filter
    "growth_enabled":      False,   # OFF: turnarounds can have neg growth
    "governance_enabled":  True,    # ON:  Indian smallcap-specific risks (pledge etc.)
    "ownership_enabled":   False,   # OFF: yfinance ownership data is unreliable for IN

    # ---- Valuation ----
    "pe_absolute_max":        100.0,   # reject only if BOTH abs AND sector-rel fail
    "pe_sector_multiple_max":   3.0,   # P/E > 3× sector median AND > abs max → reject
    "pb_absolute_max":         15.0,   # warns (not rejects)
    "ev_ebitda_max":           30.0,   # EV/EBITDA absolute cap (with sector-rel check)
    "ev_ebitda_sector_multiple_max": 3.0,  # AND > 3× sector median → reject
    "peg_max":                  3.0,   # PEG > 3 → reject (growth doesn't justify multiple)

    # ---- Quality (non-financials get leverage checks too) ----
    "roe_min_%":                5.0,   # chronic sub-5% ROE → reject
    "roce_min_%":              10.0,   # capital destruction floor (non-financials only)
    "debt_to_equity_max":       3.0,   # extreme leverage (non-financials only)
    "interest_cover_min":       1.5,   # EBIT/Interest floor (non-financials only)
    "current_ratio_min":        0.8,   # liquidity floor (non-financials only)

    # ---- Growth ----
    "yoy_rev_decline_max_%":  -20.0,   # reject if YoY REV decline worse than this ...
    "yoy_rev_decline_streak":    2,    # ... for at least N consecutive quarters
    "pat_yoy_decline_max_%":  -25.0,   # reject if YoY PAT decline worse than this ...
    "pat_yoy_decline_streak":    2,    # ... for at least N consecutive quarters

    # ---- Governance (needs governance_overrides.csv for pledge / auditor / RPT) ----
    "promoter_pledge_max_%":   40.0,   # pledge > 40% → reject (strict = 25)
    "promoter_holding_min_%":  15.0,   # promoter < 15% → warn (widely-held / exited)
    "flag_auditor_qualified":  True,   # auditor qualification → reject
    "flag_rpt_concern":        True,   # related-party transactions flagged → reject

    # ---- Ownership flow (from override CSV — quarterly FII / DII / MF delta) ----
    "fii_delta_qoq_min_pp":    -3.0,   # FII holding drop > 3pp QoQ → warn
    "dii_delta_qoq_min_pp":    -3.0,   # DII holding drop > 3pp QoQ → warn
    "mf_delta_qoq_min_pp":     -3.0,   # MF  holding drop > 3pp QoQ → warn

    # ---- Missing-data policy ----
    "strict_mode": False,              # True = no data ⇒ reject; False = no data ⇒ warn
}

# NSE Industry values corresponding to LENDERS / INSURERS.
# For these, D/E, interest cover, current ratio checks are skipped.
# (Banks by definition run 8–12× "D/E"; the metric is meaningless for them.)
FINANCIAL_SECTORS = {
    "Financial Services", "Financial Services (Banks)", "Insurance",
    "Banks", "Housing Finance", "NBFC", "Non-Banking Financial Company",
    "Capital Markets",
}


# ======================================================================================
#  2. OVERRIDES — user-supplied governance data yfinance can't provide
# ======================================================================================
def load_overrides(path: str = "governance_overrides.csv") -> dict:
    """Load user-supplied governance data from a CSV next to this file.
    Missing file → {}. Never raises.

    Expected columns (only 'ticker' is required):
        ticker, promoter_pledge_pct, promoter_holding_pct,
        fii_delta_qoq, auditor_qualified, note

    Returns {TICKER_UPPER: {field: value}} — .NS / .BO suffix stripped.
    """
    full = path if os.path.isabs(path) else \
           os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(full):
        return {}
    try:
        df = pd.read_csv(full, comment="#", skip_blank_lines=True)
        df.columns = [c.strip().lower() for c in df.columns]
        if "ticker" not in df.columns:
            return {}
        out = {}
        for _, row in df.iterrows():
            t = str(row["ticker"]).strip().upper() \
                                  .replace(".NS", "").replace(".BO", "")
            if not t:
                continue
            rec = {}
            for k in ("promoter_pledge_pct", "promoter_holding_pct",
                     "fii_delta_qoq", "dii_delta_qoq", "mf_delta_qoq",
                     "auditor_qualified", "rpt_concern"):
                v = row.get(k, np.nan)
                if pd.notna(v):
                    rec[k] = int(v) if k in ("auditor_qualified", "rpt_concern") \
                                    else float(v)
            out[t] = rec
        return out
    except Exception:
        return {}


# ======================================================================================
#  3. FETCH — pull raw fundamentals from yfinance (24-hour cache)
# ======================================================================================
def _num(x):
    """Coerce to float; return np.nan on failure or non-finite."""
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)  # 24h — fundamentals don't move intraday
def fetch_fundamentals(ticker_yahoo: str) -> dict:
    """Pull the raw fundamental fields we need for the gate. Never raises;
    on failure returns {'_error': ...}. Missing fields are np.nan.

    Note: yfinance ROE is decimal form (0.15 = 15%); D/E is percent form
    (128 = 1.28). We normalise both to human-readable units below.
    """
    if yf is None:
        return {"_error": "yfinance unavailable"}
    out = {}
    try:
        t = yf.Ticker(ticker_yahoo)
        info = t.info if hasattr(t, "info") else {}
    except Exception as e:
        return {"_error": f"info fetch: {str(e)[:60]}"}

    # ---- Valuation ----
    out["pe"]         = _num(info.get("trailingPE"))
    out["fwd_pe"]     = _num(info.get("forwardPE"))
    out["pb"]         = _num(info.get("priceToBook"))
    out["ev_ebitda"]  = _num(info.get("enterpriseToEbitda"))
    out["peg"]        = _num(info.get("pegRatio"))            # NEW: growth-adjusted P/E
    out["trailing_eps"] = _num(info.get("trailingEps"))       # NEW
    out["forward_eps"]  = _num(info.get("forwardEps"))        # NEW
    out["market_cap"]   = _num(info.get("marketCap"))

    # ---- Quality (unit normalisation — see docstring) ----
    roe_raw = _num(info.get("returnOnEquity"))
    out["roe"] = roe_raw * 100 if pd.notna(roe_raw) else np.nan
    de_raw = _num(info.get("debtToEquity"))
    out["de"] = de_raw / 100 if pd.notna(de_raw) else np.nan
    out["current_ratio"] = _num(info.get("currentRatio"))
    out["op_margin"]     = _num(info.get("operatingMargins"))
    out["profit_margin"] = _num(info.get("profitMargins"))
    out["fcf"]           = _num(info.get("freeCashflow"))

    # ---- Growth: YoY REVENUE AND PAT over recent quarters ----
    # Quarterly income statement has quarter-dates as columns.
    # We need same-quarter-prior-year growth for the most recent 4 quarters.
    out["yoy_rev_growth_recent"] = []
    out["yoy_pat_growth_recent"] = []           # NEW
    try:
        q = t.quarterly_income_stmt
        if q is not None and not q.empty:
            # Revenue YoY
            if "Total Revenue" in q.index:
                rev = q.loc["Total Revenue"].dropna().sort_index()  # ascending
                if len(rev) >= 5:
                    yoy = []
                    for i in range(len(rev) - 1, 3, -1):
                        prev, cur = rev.iloc[i - 4], rev.iloc[i]
                        if pd.notna(prev) and prev != 0:
                            yoy.append(float((cur / prev - 1) * 100))
                        if len(yoy) >= 4:
                            break
                    out["yoy_rev_growth_recent"] = yoy
            # PAT (Net Income) YoY — signed, handles loss years correctly
            for pat_key in ("Net Income", "Net Income Common Stockholders",
                            "NetIncome", "Net Income From Continuing Operations"):
                if pat_key in q.index:
                    ni = q.loc[pat_key].dropna().sort_index()
                    if len(ni) >= 5:
                        yoy = []
                        for i in range(len(ni) - 1, 3, -1):
                            prev, cur = ni.iloc[i - 4], ni.iloc[i]
                            if pd.notna(prev) and pd.notna(cur) and prev != 0:
                                # signed % change relative to |prev| — handles
                                # loss-to-profit and profit-to-loss transitions
                                yoy.append(float((cur - prev) / abs(prev) * 100))
                            if len(yoy) >= 4:
                                break
                        out["yoy_pat_growth_recent"] = yoy
                    break
    except Exception:
        pass

    # ---- Annual income & balance sheet: for Interest Cover AND ROCE ----
    out["interest_cover"] = np.nan
    out["roce"] = np.nan                        # NEW
    try:
        ann = t.income_stmt
        bs  = t.balance_sheet
        # ---- Interest Cover: EBIT / |Interest Expense| ----
        ebit_val = np.nan
        if ann is not None and not ann.empty:
            latest_i = ann.columns[0]
            for k in ("EBIT", "Operating Income", "Ebit"):
                if k in ann.index:
                    ebit_val = _num(ann.loc[k, latest_i])
                    if pd.notna(ebit_val):
                        break
            int_exp = np.nan
            for k in ("Interest Expense", "InterestExpense",
                      "Interest Expense Non Operating"):
                if k in ann.index:
                    int_exp = _num(ann.loc[k, latest_i])
                    if pd.notna(int_exp):
                        break
            if pd.notna(ebit_val) and pd.notna(int_exp) and int_exp != 0:
                out["interest_cover"] = float(ebit_val) / abs(float(int_exp))

        # ---- ROCE (NEW): EBIT / Capital Employed × 100 ----
        # Capital Employed = Total Assets − Current Liabilities
        if pd.notna(ebit_val) and bs is not None and not bs.empty:
            latest_b = bs.columns[0]
            total_assets = np.nan
            for k in ("Total Assets", "TotalAssets"):
                if k in bs.index:
                    total_assets = _num(bs.loc[k, latest_b])
                    if pd.notna(total_assets):
                        break
            curr_liab = np.nan
            for k in ("Current Liabilities", "Total Current Liabilities",
                      "CurrentLiabilities", "Other Current Liabilities"):
                if k in bs.index:
                    curr_liab = _num(bs.loc[k, latest_b])
                    if pd.notna(curr_liab):
                        break
            if pd.notna(total_assets) and pd.notna(curr_liab):
                cap_employed = total_assets - curr_liab
                if cap_employed > 0:
                    out["roce"] = (float(ebit_val) / cap_employed) * 100
    except Exception:
        pass

    # ---- Ownership (weak yfinance proxies — real data comes from override CSV) ----
    out["insider_pct_yf"]     = _num(info.get("heldPercentInsiders"))
    out["institution_pct_yf"] = _num(info.get("heldPercentInstitutions"))

    return out


# ======================================================================================
#  4. SECTOR MEDIANS — used for relative-valuation checks
# ======================================================================================
def compute_sector_medians(fundamentals: dict, sector_by_bare: dict) -> dict:
    """From {bare_ticker: raw_fund_dict} + {bare_ticker: sector}, compute the
    per-sector median for the metrics used in relative-valuation checks.
    Sectors with fewer than 5 samples fall back to universe-wide median."""
    fields = ("pe", "pb", "ev_ebitda", "roe", "roce", "de")
    rows = []
    for t, f in fundamentals.items():
        if not isinstance(f, dict) or "_error" in f:
            continue
        rec = {"ticker": t, "sector": sector_by_bare.get(t, "UNKNOWN")}
        for k in fields:
            rec[k] = f.get(k, np.nan)
        rows.append(rec)
    if not rows:
        return {}
    df = pd.DataFrame(rows)
    med = {}
    for sec, sub in df.groupby("sector"):
        if len(sub) < 5 and sec != "UNKNOWN":
            continue
        med[sec] = {k: float(sub[k].median()) for k in fields
                    if pd.notna(sub[k].median())}
    med["_ALL"] = {k: float(df[k].median()) for k in fields
                   if pd.notna(df[k].median())}
    return med


# ======================================================================================
#  5. THE GATE — apply the no-trade filter to a single stock
# ======================================================================================
def screen_fundamentals(ticker_bare: str, sector: str,
                        fund: dict, sector_medians: dict,
                        overrides: dict, config: dict) -> dict:
    """Return {status, reasons, warnings, data} where:
       status ∈ {"pass", "reject", "pass_no_data"}
       reasons = list of hard-reject rationales (empty ⇒ pass)
       warnings = list of soft flags (never trigger reject alone)
       data = the numeric fundamentals we actually evaluated
    """
    reasons, warns, data = [], [], {}
    cfg = config
    is_financial = sector in FINANCIAL_SECTORS
    ov = overrides.get(ticker_bare.upper(), {})

    # ---- 5.0 Missing-data policy ----
    if not isinstance(fund, dict) or "_error" in fund:
        if cfg.get("strict_mode"):
            return {"status": "reject", "reasons": ["no fundamental data"],
                    "warnings": [], "data": {}}
        return {"status": "pass_no_data", "reasons": [],
                "warnings": ["no fundamental data (yfinance)"], "data": {}}

    # ---- 5a. VALUATION ----
    if cfg.get("valuation_enabled"):
        sec_med = sector_medians.get(sector, sector_medians.get("_ALL", {}))
        # P/E: absolute + sector-relative
        pe = fund.get("pe")
        if pd.notna(pe) and pe > 0:
            data["pe"] = round(pe, 2)
            sec_pe = sec_med.get("pe")
            if (pe > cfg["pe_absolute_max"] and sec_pe
                    and pe > cfg["pe_sector_multiple_max"] * sec_pe):
                reasons.append(f"P/E {pe:.0f} > abs cap {cfg['pe_absolute_max']:.0f} "
                               f"AND {pe/sec_pe:.1f}× sector median ({sec_pe:.0f})")
        # P/B: absolute (warn)
        pb = fund.get("pb")
        if pd.notna(pb):
            data["pb"] = round(pb, 2)
            if pb > cfg["pb_absolute_max"]:
                warns.append(f"P/B {pb:.1f} > {cfg['pb_absolute_max']:.0f} (rich)")
        # EV/EBITDA: absolute + sector-relative (NEW gate)
        eb = fund.get("ev_ebitda")
        if pd.notna(eb) and eb > 0:
            data["ev_ebitda"] = round(eb, 2)
            sec_eb = sec_med.get("ev_ebitda")
            if (eb > cfg["ev_ebitda_max"] and sec_eb
                    and eb > cfg["ev_ebitda_sector_multiple_max"] * sec_eb):
                reasons.append(f"EV/EBITDA {eb:.0f} > abs cap {cfg['ev_ebitda_max']:.0f} "
                               f"AND {eb/sec_eb:.1f}× sector median ({sec_eb:.0f})")
        # PEG (NEW gate) — growth-adjusted P/E
        peg = fund.get("peg")
        if pd.notna(peg) and peg > 0:
            data["peg"] = round(peg, 2)
            if peg > cfg["peg_max"]:
                reasons.append(f"PEG {peg:.1f} > {cfg['peg_max']:.1f} "
                               f"(growth doesn't justify multiple)")

    # ---- 5b. QUALITY ----
    if cfg.get("quality_enabled"):
        roe = fund.get("roe")
        if pd.notna(roe):
            data["roe_%"] = round(roe, 2)
            if roe < cfg["roe_min_%"]:
                reasons.append(f"ROE {roe:.1f}% < {cfg['roe_min_%']:.0f}% floor")
        # Leverage / solvency / capital-efficiency checks — non-financials only
        if not is_financial:
            # ROCE (NEW gate) — capital-destruction check
            roce = fund.get("roce")
            if pd.notna(roce):
                data["roce_%"] = round(roce, 2)
                if roce < cfg["roce_min_%"]:
                    reasons.append(f"ROCE {roce:.1f}% < {cfg['roce_min_%']:.0f}% floor "
                                   f"(capital destruction)")
            de = fund.get("de")
            if pd.notna(de):
                data["de"] = round(de, 2)
                if de > cfg["debt_to_equity_max"]:
                    reasons.append(f"D/E {de:.1f} > {cfg['debt_to_equity_max']:.1f} ceiling")
            ic = fund.get("interest_cover")
            if pd.notna(ic):
                data["interest_cover"] = round(ic, 2)
                if ic < cfg["interest_cover_min"]:
                    reasons.append(f"Interest cover {ic:.1f}× < "
                                   f"{cfg['interest_cover_min']:.1f}× (debt-service risk)")
            cr = fund.get("current_ratio")
            if pd.notna(cr):
                data["current_ratio"] = round(cr, 2)
                if cr < cfg["current_ratio_min"]:
                    reasons.append(f"Current ratio {cr:.2f} < "
                                   f"{cfg['current_ratio_min']:.2f} (liquidity strain)")

    # ---- 5c. GROWTH ----
    if cfg.get("growth_enabled"):
        # Revenue decline streak
        yoy = fund.get("yoy_rev_growth_recent", [])
        if yoy:
            data["yoy_rev_%_recent"] = [round(x, 1) for x in yoy[:4]]
            floor = cfg["yoy_rev_decline_max_%"]
            need  = cfg["yoy_rev_decline_streak"]
            streak = 0
            for g in yoy:                       # leading (most-recent) run
                if g < floor:
                    streak += 1
                else:
                    break
            if streak >= need:
                reasons.append(f"Revenue YoY worse than {floor:.0f}% for "
                               f"{streak} consecutive quarters")
        # PAT decline streak (NEW gate) — earnings trajectory
        yoy_pat = fund.get("yoy_pat_growth_recent", [])
        if yoy_pat:
            data["yoy_pat_%_recent"] = [round(x, 1) for x in yoy_pat[:4]]
            floor_p = cfg["pat_yoy_decline_max_%"]
            need_p  = cfg["pat_yoy_decline_streak"]
            streak_p = 0
            for g in yoy_pat:
                if pd.notna(g) and g < floor_p:
                    streak_p += 1
                else:
                    break
            if streak_p >= need_p:
                reasons.append(f"PAT YoY worse than {floor_p:.0f}% for "
                               f"{streak_p} consecutive quarters")

    # ---- 5d. GOVERNANCE (needs governance_overrides.csv for pledge / auditor / RPT) ----
    if cfg.get("governance_enabled"):
        pledge    = ov.get("promoter_pledge_pct")
        prom_hold = ov.get("promoter_holding_pct")
        if pledge is not None:
            data["promoter_pledge_%"] = round(pledge, 2)
            if pledge > cfg["promoter_pledge_max_%"]:
                reasons.append(f"Promoter pledge {pledge:.0f}% > "
                               f"{cfg['promoter_pledge_max_%']:.0f}% (governance risk)")
        else:
            warns.append("promoter pledge unknown (add to governance_overrides.csv)")
        if prom_hold is not None:
            data["promoter_holding_%"] = round(prom_hold, 2)
            if prom_hold < cfg["promoter_holding_min_%"]:
                warns.append(f"Promoter holding {prom_hold:.0f}% < "
                             f"{cfg['promoter_holding_min_%']:.0f}% (widely-held or exited)")
        if cfg.get("flag_auditor_qualified") and ov.get("auditor_qualified"):
            reasons.append("Auditor has qualified opinion (from override CSV)")
        # RPT concern (NEW) — user-flagged related-party transaction risk
        if cfg.get("flag_rpt_concern") and ov.get("rpt_concern"):
            reasons.append("Related-party transactions flagged as concerning "
                           "(from override CSV)")

    # ---- 5e. OWNERSHIP FLOW (override CSV only — yfinance IN data too flaky) ----
    if cfg.get("ownership_enabled"):
        fii_d = ov.get("fii_delta_qoq")
        if fii_d is not None:
            data["fii_delta_qoq_pp"] = round(fii_d, 2)
            if fii_d < cfg["fii_delta_qoq_min_pp"]:
                warns.append(f"FII cut holding by {abs(fii_d):.1f}pp QoQ")
        # DII delta (NEW)
        dii_d = ov.get("dii_delta_qoq")
        if dii_d is not None:
            data["dii_delta_qoq_pp"] = round(dii_d, 2)
            if dii_d < cfg["dii_delta_qoq_min_pp"]:
                warns.append(f"DII cut holding by {abs(dii_d):.1f}pp QoQ")
        # MF delta (NEW)
        mf_d = ov.get("mf_delta_qoq")
        if mf_d is not None:
            data["mf_delta_qoq_pp"] = round(mf_d, 2)
            if mf_d < cfg["mf_delta_qoq_min_pp"]:
                warns.append(f"MF cut holding by {abs(mf_d):.1f}pp QoQ")

    status = "reject" if reasons else "pass"
    return {"status": status, "reasons": reasons, "warnings": warns, "data": data}


# ======================================================================================
#  6. BATCH — run the gate over the whole universe (two-pass, sector-median-aware)
# ======================================================================================
def _bare(ticker_yahoo: str) -> str:
    return ticker_yahoo.replace(".NS", "").replace(".BO", "").upper()


def screen_universe(tickers_yahoo: list, sector_map: dict, config: dict,
                    progress_cb=None) -> tuple:
    """Two-pass screen over a universe.
       Pass 1: fetch fundamentals for every stock (24h cached).
       Pass 2: compute sector medians, then apply gate to each stock.

    Args
        tickers_yahoo : ["HUDCO.NS", "IRFC.NS", ...]
        sector_map    : {"HUDCO": "Financial Services", ...}  (bare-ticker keys)
        config        : dict, typically DEFAULT_FUNDA_CONFIG with user overrides
        progress_cb   : optional callable(k, n, symbol) for a Streamlit progress bar

    Returns
        (results, sector_medians)
        results = {bare_ticker: {status, reasons, warnings, data}}
        sector_medians = {sector_name: {pe: x, pb: y, ...}}  (empty if valuation off)
    """
    overrides = load_overrides()
    fundamentals = {}
    n = len(tickers_yahoo)
    for k, ty in enumerate(tickers_yahoo):
        if progress_cb:
            progress_cb(k, n, ty)
        fundamentals[_bare(ty)] = fetch_fundamentals(ty)

    sec_by_bare = {_bare(ty): sector_map.get(_bare(ty), "UNKNOWN")
                   for ty in tickers_yahoo}

    medians = (compute_sector_medians(fundamentals, sec_by_bare)
               if config.get("valuation_enabled") else {})

    results = {}
    for ty in tickers_yahoo:
        b = _bare(ty)
        results[b] = screen_fundamentals(b, sec_by_bare[b],
                                         fundamentals.get(b, {}),
                                         medians, overrides, config)
    return results, medians


# ======================================================================================
#  7. SUMMARY helpers for the UI (optional but handy)
# ======================================================================================
def summarize_results(results: dict) -> dict:
    """Roll-up for the sidebar / results header."""
    n = len(results)
    if n == 0:
        return {"total": 0, "pass": 0, "reject": 0, "no_data": 0, "warn_only": 0}
    passed  = sum(1 for r in results.values() if r["status"] == "pass")
    rejected = sum(1 for r in results.values() if r["status"] == "reject")
    no_data  = sum(1 for r in results.values() if r["status"] == "pass_no_data")
    warn_only = sum(1 for r in results.values()
                    if r["status"] == "pass" and r["warnings"])
    return {"total": n, "pass": passed, "reject": rejected,
            "no_data": no_data, "warn_only": warn_only}


def rejects_to_dataframe(results: dict) -> pd.DataFrame:
    """Build a DataFrame of the rejected names for display in the UI."""
    rows = []
    for tick, r in results.items():
        if r["status"] != "reject":
            continue
        rows.append({
            "ticker": tick,
            "reasons": " | ".join(r["reasons"]),
            "warnings": " | ".join(r["warnings"]),
            **r["data"],
        })
    return pd.DataFrame(rows)
