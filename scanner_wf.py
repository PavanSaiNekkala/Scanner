"""
NSE Market-Wide Swing Scanner  (daily, after-market)
====================================================
Runs the single-stock engine (260706_swing_screener_app.py) across a whole universe of NSE
stocks, backtests each over its available history, and shortlists the names whose
signal fires *today* — i.e. candidates to buy at tomorrow's open for a ~10%+ swing in
7-15 days. Each candidate carries its historical backtest stats as a confidence measure.

Run with:  streamlit run swing_scanner_app.py
  (keep 260706_swing_screener_app.py in the same folder - this imports its engine)

Optional: place a `universe.csv` next to this file with columns [ticker, bucket]
          (bucket = LargeCap / MidCap / SmallCap / Nifty500) to override the built-in list.
"""

import os
import io
import time
import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st

try:
    import requests
except Exception:
    requests = None

import importlib.util

# --- Locate the strategy engine (the screener file) ---
# Auto-discover any "*screener*.py" beside this file and use the MOST RECENTLY MODIFIED one,
# so the scanner always runs the current engine. Uses os.listdir (not glob) so that spaces or
# special characters in the folder path can never break the match.
_here = os.path.dirname(os.path.abspath(__file__))
_self = os.path.basename(os.path.abspath(__file__)).lower()

def _find_engine(folder: str):
    try:
        names = os.listdir(folder)
    except Exception:
        names = []
    cands = []
    for nm in names:
        low = nm.lower()
        if not low.endswith(".py"):
            continue
        if low == _self:                 # never import ourselves
            continue
        if "screener" not in low:        # case-insensitive match
            continue
        full = os.path.join(folder, nm)
        if os.path.isfile(full):
            cands.append(full)
    return cands, names

_matches, _seen = _find_engine(_here)
if not _matches:
    _pys = [n for n in _seen if n.lower().endswith(".py")] or ["(none)"]
    raise FileNotFoundError(
        "No screener engine found.\n"
        f"  Looking in : {_here}\n"
        f"  This file  : {_self}\n"
        f"  .py files seen here: {', '.join(_pys)}\n"
        "  Fix: put the swing screener .py file (any name containing 'screener') in this exact "
        "folder, and launch streamlit from this folder."
    )
_ENGINE_PATH = max(_matches, key=os.path.getmtime)   # newest = current
ENGINE_FILE = os.path.basename(_ENGINE_PATH)
_spec = importlib.util.spec_from_file_location("engine", _ENGINE_PATH)
engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(engine)

try:
    import yfinance as yf
except Exception:
    yf = None


# ======================================================================================
#  UNIVERSE  - built-in default lists (override with universe.csv if present)
# ======================================================================================
BUILTIN_UNIVERSE = {
    "LargeCap": [
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN",
        "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "BAJFINANCE", "ASIANPAINT", "MARUTI",
        "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO", "NESTLEIND", "ONGC", "NTPC", "POWERGRID",
        "M&M", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA",
        "HCLTECH", "BAJAJFINSV", "TECHM", "GRASIM", "HINDALCO", "DRREDDY", "CIPLA", "BPCL",
        "BRITANNIA", "EICHERMOT", "DIVISLAB", "HEROMOTOCO", "INDUSINDBK", "APOLLOHOSP",
        "TATACONSUM", "BAJAJ-AUTO", "SBILIFE", "HDFCLIFE", "LTIM", "SHRIRAMFIN",
    ],
    "MidCap": [
        "HUDCO", "IRFC", "RVNL", "BEL", "BHEL", "IOC", "GAIL", "PFC", "RECLTD", "IRCTC",
        "ABCAPITAL", "ASHOKLEY", "AUROPHARMA", "BANKBARODA", "CANBK", "CGPOWER", "CONCOR",
        "COFORGE", "CUMMINSIND", "DLF", "GODREJPROP", "HAVELLS", "INDHOTEL", "JUBLFOOD",
        "LICHSGFIN", "LUPIN", "MRF", "NMDC", "OBEROIRLTY", "PAGEIND", "PERSISTENT",
        "PIIND", "POLYCAB", "SAIL", "SUZLON", "TATAPOWER", "TORNTPHARM", "TRENT", "VBL",
        "YESBANK", "IDFCFIRSTB", "PNB", "UNIONBANK", "MAXHEALTH", "LODHA", "HINDZINC",
    ],
    "SmallCap": [
        "IREDA", "MAZDOCK", "COCHINSHIP", "GRSE", "HAL", "BDL", "MIDHANI", "RITES",
        "IRCON", "NBCC", "ENGINERSIN", "HFCL", "GMRINFRA", "JWL", "KALYANKJIL", "KAYNES",
        "TATATECH", "ZOMATO", "NYKAA", "PAYTM", "POLICYBZR", "DELHIVERY", "MAPMYINDIA",
        "IEX", "CDSL", "BSE", "ANGELONE", "CAMS", "KFINTECH", "MCX", "INTELLECT",
        "TANLA", "ROUTE", "HAPPSTMNDS", "LATENTVIEW", "SONACOMS", "OLECTRA",
    ],
}
BUILTIN_UNIVERSE["Nifty500"] = sorted(set(sum(BUILTIN_UNIVERSE.values(), [])))


# --- Official NSE index constituent CSVs (the full, current lists) ---
NSE_INDEX_CSV = {
    "Nifty500":    "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
    "LargeCap":    "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
    "MidCap":      "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "SmallCap":    "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
}
_NSE_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"),
    "Accept": "text/csv,application/csv,application/vnd.ms-excel,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _nse_csv(url: str) -> list:
    """Fetch an NSE index constituent CSV. NSE blocks bare requests, so we send browser
    headers and first prime cookies by hitting the homepage."""
    if requests is None:
        raise RuntimeError("requests not installed")
    s = requests.Session()
    s.headers.update(_NSE_HEADERS)
    try:                                   # prime cookies (NSE requires a prior page hit)
        s.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass
    r = s.get(url, timeout=20)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip() for c in df.columns]
    col = "Symbol" if "Symbol" in df.columns else df.columns[2]
    return sorted({str(x).strip().upper() for x in df[col] if str(x).strip()})


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_nse_universe():
    """Build the full universe from live NSE index lists; raise if any core list fails."""
    buckets = {name: _nse_csv(url) for name, url in NSE_INDEX_CSV.items()}
    # 'AllNSE' = union of the three broad indices (dedup)
    buckets["AllNSE"] = sorted(set(buckets["Nifty500"]) | set(buckets["MidCap"]) | set(buckets["SmallCap"]))
    return buckets


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_sector_map() -> dict:
    """Build {SYMBOL: Industry} from the NSE index CSVs (they carry an 'Industry' column).
    Free — same source we already use for the universe. Returns {} if NSE is unreachable."""
    if requests is None:
        return {}
    smap = {}
    s = requests.Session()
    s.headers.update(_NSE_HEADERS)
    try:
        s.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass
    for url in NSE_INDEX_CSV.values():
        try:
            r = s.get(url, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            df.columns = [c.strip() for c in df.columns]
            if "Symbol" not in df.columns or "Industry" not in df.columns:
                continue
            for sym, ind in zip(df["Symbol"], df["Industry"]):
                sym = str(sym).strip().upper()
                ind = str(ind).strip()
                if sym and ind and sym not in smap:
                    smap[sym] = ind
        except Exception:
            continue
    return smap


def apply_sector_caps(cand: pd.DataFrame, max_per_sector: int) -> tuple:
    """Keep at most `max_per_sector` names per sector, preferring the highest-ranked.
    Assumes `cand` is already sorted best-first. UNKNOWN sectors are never capped
    (we can't claim concentration we can't measure)."""
    if max_per_sector <= 0 or cand.empty:
        return cand, {}
    kept_idx, counts, dropped = [], {}, {}
    for i, row in cand.iterrows():
        sec = row.get("sector", "UNKNOWN") or "UNKNOWN"
        if sec == "UNKNOWN":
            kept_idx.append(i)
            continue
        c = counts.get(sec, 0)
        if c < max_per_sector:
            counts[sec] = c + 1
            kept_idx.append(i)
        else:
            dropped[sec] = dropped.get(sec, 0) + 1
    return cand.loc[kept_idx], dropped


def load_universe():
    """Priority: user universe.csv  >  live NSE index CSVs  >  built-in fallback."""
    path = os.path.join(os.path.dirname(__file__), "universe.csv")
    if os.path.exists(path):
        try:
            u = pd.read_csv(path)
            u.columns = [c.strip().lower() for c in u.columns]
            buckets = {b: [str(t).strip().upper() for t in sub["ticker"]]
                       for b, sub in u.groupby("bucket")}
            if "Nifty500" not in buckets:
                buckets["Nifty500"] = sorted(set(sum(buckets.values(), [])))
            return buckets, "universe.csv (your file)"
        except Exception as e:
            st.warning(f"Could not read universe.csv ({e}); trying live NSE lists.")
    try:
        return fetch_nse_universe(), "live NSE index CSVs"
    except Exception as e:
        st.warning(f"Could not reach NSE ({str(e)[:60]}). Using the built-in sample list. "
                   "Re-run to retry, or add a universe.csv.")
        return BUILTIN_UNIVERSE, "built-in fallback list"


def to_yahoo(sym: str) -> str:
    sym = sym.strip().upper()
    return sym if sym.endswith((".NS", ".BO")) else sym + ".NS"


# ======================================================================================
#  PER-STOCK SCAN
# ======================================================================================
MIN_DAYS = 250
TARGET_YEARS = 10
RS_WINDOW = 63                       # ~3 months for relative-strength
BENCH_TICKERS = ["^CRSLDX", "^NSEI"] # Nifty 500 (broad), fallback Nifty 50
# Segment indices: your universe lives here, not in the IT mega-caps that can lift the headline.
# Several candidates each — Yahoo's coverage of Indian segment indices is inconsistent.
SEGMENT_TICKERS = {
    "MidCap":   ["^NSEMDCP50", "NIFTY_MIDCAP_100.NS", "^CNXMIDCAP"],
    "SmallCap": ["^CNXSC", "NIFTYSMLCAP250.NS", "^CNXSMCAP"],
}


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_one(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df.dropna()


@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def fetch_index(start: dt.date, end: dt.date):
    """Fetch a broad benchmark index (Nifty 500, fallback Nifty 50) for regime + RS."""
    if yf is None:
        return None, pd.DataFrame()
    for t in BENCH_TICKERS:
        try:
            df = yf.Ticker(t).history(start=start, end=end, interval="1d", auto_adjust=True)
            if df is not None and not df.empty:
                df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
                df.index = pd.to_datetime(df.index).tz_localize(None)
                return t, df.dropna()
        except Exception:
            continue
    return None, pd.DataFrame()


@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def fetch_segments(start: dt.date, end: dt.date) -> dict:
    """Fetch mid/small-cap segment indices. Returns {name: pct_vs_200dma} for those that resolve."""
    out = {}
    if yf is None:
        return out
    for seg, candidates in SEGMENT_TICKERS.items():
        for t in candidates:
            try:
                df = yf.Ticker(t).history(start=start, end=end, interval="1d", auto_adjust=True)
                if df is None or df.empty or len(df) < 210:
                    continue
                c = df["Close"].dropna()
                s200 = c.rolling(200).mean().iloc[-1]
                if not np.isfinite(s200):
                    continue
                out[seg] = {"ticker": t,
                            "pct_vs_200": round(float(c.iloc[-1] / s200 - 1) * 100, 2),
                            "above_200": bool(c.iloc[-1] > s200)}
                break
            except Exception:
                continue
    return out


def compute_breadth(rows: list) -> dict:
    """Advance/decline breadth computed from the scanned universe itself (no extra fetches).
    This is the piece that catches a narrow, breadth-negative day behind a green headline index."""
    ok = [r for r in rows if r.get("status") == "ok" and np.isfinite(r.get("day_chg_%", np.nan))]
    n = len(ok)
    if n == 0:
        return {"status": "UNKNOWN", "n": 0}
    adv = sum(1 for r in ok if r["day_chg_%"] > 0)
    dec = sum(1 for r in ok if r["day_chg_%"] < 0)
    above50 = sum(1 for r in ok if r.get("above_50dma"))
    ad_ratio = adv / max(dec, 1)
    pct_adv = 100 * adv / n
    pct_above50 = 100 * above50 / n
    # negative breadth: most names fell today, or most sit below their own 50-DMA
    if pct_adv >= 55 and pct_above50 >= 50:
        status = "POSITIVE"
    elif pct_adv < 40 or pct_above50 < 40:
        status = "NEGATIVE"
    else:
        status = "MIXED"
    return {"status": status, "n": n, "advancers": adv, "decliners": dec,
            "pct_advancers": round(pct_adv, 1), "pct_above_50dma": round(pct_above50, 1),
            "ad_ratio": round(ad_ratio, 2)}


def compute_regime(idx_df: pd.DataFrame) -> dict:
    """Trend/momentum of the broad benchmark (one input to the composite gate)."""
    if idx_df.empty or len(idx_df) < 210:
        return {"status": "UNKNOWN", "note": "index data unavailable",
                "idx_ret_window": 0.0, "index_ok": False}
    c = idx_df["Close"]
    s200 = c.rolling(200).mean().iloc[-1]
    last = float(c.iloc[-1])
    above200 = bool(last > s200) if np.isfinite(s200) else True
    pct_vs200 = (last / s200 - 1) * 100 if np.isfinite(s200) else np.nan
    roc10 = (c.iloc[-1] / c.iloc[-11] - 1) * 100 if len(c) > 11 else 0.0
    idx_ret_window = (c.iloc[-1] / c.iloc[-(RS_WINDOW + 1)] - 1) * 100 if len(c) > RS_WINDOW else 0.0
    if above200 and roc10 > -1.0:
        status = "RISK-ON"
    elif above200 or roc10 > -3.0:
        status = "NEUTRAL"
    else:
        status = "RISK-OFF"
    return {"status": status, "above_200": above200, "pct_vs_200": round(float(pct_vs200), 2),
            "roc10": round(float(roc10), 2), "idx_ret_window": float(idx_ret_window),
            "last": round(last, 2), "index_ok": True}


def composite_gate(regime: dict, segments: dict, breadth: dict) -> dict:
    """Combine index trend + segment trend + breadth into one verdict.

    Crucially, negative BREADTH can force RISK-OFF even when the headline index is green —
    the exact scenario where a basket of longs sinks behind a mega-cap-driven index.
    """
    idx_state = regime.get("status", "UNKNOWN")
    br = breadth.get("status", "UNKNOWN")
    seg_below = [s for s, v in segments.items() if not v.get("above_200", True)]

    score = 0
    if idx_state == "RISK-ON":  score += 1
    elif idx_state == "RISK-OFF": score -= 1
    if br == "POSITIVE": score += 1
    elif br == "NEGATIVE": score -= 1          # breadth can veto a green index
    if seg_below: score -= 1                    # your universe's own segment is in a downtrend

    if br == "NEGATIVE" and idx_state != "RISK-ON":
        final = "RISK-OFF"
    elif score >= 2:
        final = "RISK-ON"
    elif score <= -1:
        final = "RISK-OFF"
    else:
        final = "NEUTRAL"

    reasons = [f"index {idx_state}", f"breadth {br}"]
    if seg_below:
        reasons.append(f"{'/'.join(seg_below)} below 200-DMA")
    elif segments:
        reasons.append("segments above 200-DMA")
    return {"final": final, "score": score, "reasons": reasons,
            "breadth_veto": (br == "NEGATIVE" and idx_state == "RISK-ON")}


def scan_one(ticker, start, end, strategy, p, bt_kwargs, idx_ret_window=0.0, sector_map=None) -> dict:
    try:
        raw = fetch_one(ticker, start, end)
    except Exception as e:
        return {"ticker": ticker, "status": f"fetch error: {str(e)[:40]}"}
    if raw.empty:
        return {"ticker": ticker, "status": "no data"}
    if len(raw) < MIN_DAYS:
        return {"ticker": ticker, "status": f"insufficient data ({len(raw)}d) - skipped"}

    df = engine.compute_indicators(raw)
    df = engine.generate_signals(df, strategy, p)
    trades = engine.run_backtest(df, **bt_kwargs)
    stats = engine.summarize(trades)

    yrs = (raw.index[-1] - raw.index[0]).days / 365.25
    remark = "" if yrs >= TARGET_YEARS - 0.5 else \
             f"limited history: {yrs:.1f}y (<{TARGET_YEARS}y) - lower confidence"

    last = df.iloc[-1]
    signals_today = bool(last["signal"])
    regime_today = (last.get("trade_type", "") or "UPTREND") if signals_today else ""

    n = stats.get("trades", 0)
    exp = stats.get("expectancy_%", 0.0)
    winr = stats.get("profitable_%", 0.0)
    exp_day = stats.get("exp_per_day_%", 0.0)      # return per DAY of capital deployed
    size_factor = n / (n + 30.0)
    # Confidence is built on expectancy PER DAY, because capital-rotation makes days the scarce
    # resource: a +2% trade in 3 days beats a +3% trade in 10 days.
    confidence = round(max(exp_day, 0) * (winr / 100.0) * size_factor * 100, 2)

    # --- RELATIVE STRENGTH: stock's return minus the index's over the RS window ---
    c_ser = df["Close"]
    if len(c_ser) > RS_WINDOW:
        stock_ret_window = (c_ser.iloc[-1] / c_ser.iloc[-(RS_WINDOW + 1)] - 1) * 100
    else:
        stock_ret_window = (c_ser.iloc[-1] / c_ser.iloc[0] - 1) * 100
    rel_strength = round(float(stock_ret_window - idx_ret_window), 2)   # >0 = beating the market
    # blended rank: confidence tilted by relative strength (bounded ±50%)
    rs_norm = max(min(rel_strength / 30.0, 0.5), -0.5)
    rank_score = round(confidence * (1 + rs_norm), 2)

    # --- point 1: concrete stop-loss for a trade entered ~ at the last close ---
    entry_ref = float(last["Close"])
    atr_now = float(last["atr14"]) if np.isfinite(last["atr14"]) else 0.0
    stop_mult = bt_kwargs.get("stop_value", 2.0)
    max_stop_pct = bt_kwargs.get("max_stop_pct", 8.0) or 8.0
    tgt_pct = bt_kwargs.get("target_pct", 10.0)

    # --- LIMIT ENTRY: the price to actually place the order at (don't chase the open) ---
    entry_mode = bt_kwargs.get("entry_mode", "Market open")
    limit_pct = bt_kwargs.get("limit_pct", 0.0)
    if entry_mode == "Limit":
        limit_price = round(entry_ref * (1 - limit_pct / 100.0), 2)
        plan_entry = limit_price                # stop/target computed off the price you'd pay
    else:
        limit_price = np.nan
        plan_entry = entry_ref

    stop_price = plan_entry - stop_mult * atr_now
    floor = plan_entry * (1 - max_stop_pct / 100)
    stop_price = max(stop_price, floor)                       # respect max-loss cap
    stop_pct = round((stop_price / plan_entry - 1) * 100, 2)
    target_price = round(plan_entry * (1 + tgt_pct / 100), 2)

    # --- point 2: expected days to target, from historical winners ---
    med_days = stats.get("med_days_to_target", np.nan)
    n_win = stats.get("n_winners", 0)
    if np.isnan(med_days):
        days_to_target = "n/a"
    elif n_win < 5:
        days_to_target = f"{med_days:.0f}d ⚠ thin"
    else:
        days_to_target = f"{med_days:.0f}d"

    return {
        "ticker": ticker.replace(".NS", "").replace(".BO", ""), "yahoo": ticker, "status": "ok",
        "sector": (sector_map or {}).get(ticker.replace(".NS", "").replace(".BO", "").upper(), "UNKNOWN"),
        "signals_today": signals_today, "regime_today": regime_today,
        "bt_from": raw.index[0].date(), "bt_to": raw.index[-1].date(), "years": round(yrs, 1),
        "hist_trades": n, "win_%": winr, "expectancy_%": exp,
        "avg_win_%": stats.get("avg_win_%", 0.0), "avg_loss_%": stats.get("avg_loss_%", 0.0),
        "avg_days": stats.get("avg_days", 0.0), "confidence": confidence,
        "exp_per_day_%": exp_day, "cut_exits": stats.get("cut_exits", 0),
        "trail_exits": stats.get("trail_exits", 0),
        "rel_strength": rel_strength, "rank_score": rank_score,
        # --- breadth inputs (free: computed from data already fetched) ---
        "day_chg_%": round(float(c_ser.iloc[-1] / c_ser.iloc[-2] - 1) * 100, 2) if len(c_ser) > 1 else np.nan,
        "above_50dma": bool(last["Close"] > last["sma50"]) if np.isfinite(last["sma50"]) else False,
        "last_close": round(entry_ref, 2), "last_atr_pct": round(float(last["atr_pct"]), 2),
        # point 1 outputs
        "entry_ref": round(entry_ref, 2), "limit_price": limit_price, "plan_entry": round(plan_entry, 2),
        "stop_price": round(stop_price, 2), "stop_%": stop_pct,
        "target_price": target_price,
        # point 2 output
        "exp_days_to_target": days_to_target,
        # point 3 outputs (counts + %)
        "target_hits": stats.get("target_hits", 0), "target_%": stats.get("target_pct_of_all", 0.0),
        "stop_hits": stats.get("stop_hits", 0), "stop_hit_%": stats.get("stop_pct_of_all", 0.0),
         "trail_%": stats.get("trail_pct_of_all", 0.0),
        "time_exits": stats.get("time_exits", 0), "time_%": stats.get("time_pct_of_all", 0.0),
        "time_win": stats.get("time_win", 0), "time_loss": stats.get("time_loss", 0),
        "remark": remark,
    }


# ======================================================================================
#  CHART (for click-to-view)
# ======================================================================================
def build_stock_chart(yahoo_ticker, start, end, strategy, p, bt_kwargs):
    """Recompute one stock and return a plotly price+trades figure + its trade log."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    raw = fetch_one(yahoo_ticker, start, end)
    if raw.empty:
        return None, None
    df = engine.compute_indicators(raw)
    df = engine.generate_signals(df, strategy, p)
    trades = engine.run_backtest(df, **bt_kwargs)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28],
                        vertical_spacing=0.05,
                        subplot_titles=("Close price with entries", "Cumulative net return (overlapping proxy)"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close",
                             line=dict(color="#334155", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["sma200"], name="200-DMA",
                             line=dict(color="#f59e0b", width=1, dash="dot")), row=1, col=1)
    colors = {"TARGET": "#16a34a", "TRAIL": "#86efac", "STOP": "#dc2626", "TIME": "#94a3b8"}
    if not trades.empty:
        for oc, cl in colors.items():
            sub = trades[trades["outcome"] == oc]
            if not sub.empty:
                fig.add_trace(go.Scatter(x=pd.to_datetime(sub["entry_date"]), y=sub["entry_price"],
                                         mode="markers", name=oc,
                                         marker=dict(color=cl, size=6, line=dict(width=0.4, color="white"))),
                              row=1, col=1)
        eq = trades.sort_values("entry_date").copy()
        eq["cum"] = eq["net_return_%"].cumsum()
        fig.add_trace(go.Scatter(x=pd.to_datetime(eq["entry_date"]), y=eq["cum"],
                                 name="Cumulative net %", line=dict(color="#2563eb", width=1.4)),
                      row=2, col=1)
    fig.update_layout(height=560, hovermode="x unified", legend_orientation="h",
                      margin=dict(t=40, b=10))
    return fig, trades


# ======================================================================================
#  UI
# ======================================================================================
def main():
    st.set_page_config(page_title="NSE Daily Swing Scanner", layout="wide")
    st.title("NSE Market-Wide Daily Swing Scanner")
    st.caption("Runs the swing engine across a universe of NSE stocks and shortlists names "
               "signalling today - candidates for a 10%+ move in 7-15 days. Educational tool, "
               "not investment advice. Run after market close.")
    st.caption(f"⚙️ Strategy engine loaded: **{ENGINE_FILE}** (newest `*screener*.py` in this folder)")

    universe, src = load_universe()

    with st.sidebar:
        st.header("1 - Universe")
        bucket = st.selectbox("Segment",
                              ["LargeCap", "MidCap", "SmallCap", "Nifty500", "AllNSE", "Enter manually"])
        if bucket == "Enter manually":
            txt = st.text_area("Tickers (comma/space separated)", "HUDCO, IRFC, RVNL, BEL")
            tickers = [t for t in txt.replace(",", " ").split()]
        else:
            tickers = universe.get(bucket, [])
        st.caption(f"Source: {src}. {len(tickers)} stocks in {bucket}.")
        if len(tickers) > 200:
            st.warning(f"{len(tickers)} stocks is a heavy run on free Yahoo data (expect several "
                       "minutes and some fetch failures). Consider running in batches via the limit below.")
        max_n = st.slider("Limit stocks this run", 5, max(5, len(tickers)), min(50, len(tickers)),
                          help="Yahoo rate-limits large runs. Start small; raise once stable.")

        st.header("2 - Backtest window")
        yrs = st.slider("Years of history (target)", 3, 15, TARGET_YEARS,
                        help="Expert default 10y - spans multiple bull/bear cycles. Stocks with "
                             "less history use what's available and are flagged.")
        end = dt.date.today()
        start = end - dt.timedelta(days=int(yrs * 365.25) + 300)

        st.header("3 - Strategy & rules")
        strategy = st.selectbox("Strategy", ["PASS_combined", "PASS_recommended", "PASS_tight",
                                             "PASS_balanced", "PASS_reversal"], index=0)
        target_pct = st.number_input("Target (%)", 1.0, 100.0, 15.0, 0.5)
        cA, cB = st.columns(2)
        min_hold = cA.number_input("Min hold (d)", 1, 60, 1)
        max_hold = cB.number_input("Max hold (d)", 1, 120, 30)
        entry_choice = st.radio("Entry style",
                                ["Limit near signal close (recommended)", "Market at next open"], index=0,
                                help="Market buys whatever the open gives — a gap-up means a worse fill. "
                                     "Limit places a resting buy and skips the trade if price never returns.")
        if entry_choice.startswith("Limit"):
            entry_mode = "Limit"
            limit_pct = st.slider("Limit below signal close (%)", 0.0, 5.0, 0.5, 0.1,
                                  help="0 = order at the signal close. Higher = wait for a deeper "
                                       "pullback: better fills, but more signals never fill.")
            fill_days = st.number_input("Order valid for (sessions)", 1, 5, 1)
        else:
            entry_mode, limit_pct, fill_days = "Market open", 0.0, 1
        exit_mode = st.radio("Exit style", ["Trailing", "Fixed target"], index=1,
                             help="Trailing lets winners run past the target.")
        trail_mult = st.slider("Trailing x ATR", 0.5, 5.0, 2.0, 0.5) if exit_mode == "Trailing" else 2.0
        lock_pct = st.slider("Lock profit once objective hit (%)", 0.0, 30.0, 7.0, 0.5,
                             help="After +10% is touched, the stop never falls below this. "
                                  "Protects the objective while letting the trade run to 20-30%.") \
                   if exit_mode == "Trailing" else None
        cut_on = st.checkbox("Cut dead trades early (conviction exit)", value=False,
                             help="Still red after N days -> free the capital for the next signal.")
        cut_day = st.number_input("Cut on day", 1, 10, 2) if cut_on else None
        cut_threshold = st.slider("if return below (%)", -8.0, 2.0, 0.0, 0.5) if cut_on else 0.0

        st.header("4 - Risk")
        stop_anchor = st.radio("Stop anchoring", ["ATR distance", "Structure (swing low)"],
                               help="Structure = below recent support; survives normal pullbacks "
                                    "in a channel. ATR = fixed volatility distance.")
        stop_anchor = "Structure" if stop_anchor.startswith("Structure") else "ATR"
        trail_anchor = st.radio("Trail anchoring", ["ATR distance", "Structure (rising swing low)"],
                                help="Structure trailing: bigger winners per trade, longer holds.")
        trail_anchor = "Structure" if trail_anchor.startswith("Structure") else "ATR"
        stop_value = st.slider("Stop (x ATR)", 0.5, 5.0, 2.0, 0.5)
        max_stop_pct = st.slider("Max loss cap (%)", 2.0, 20.0, 10.0, 0.5)
        max_atr_pct = st.slider("Skip if ATR% above", 3.0, 15.0, 8.0, 0.5)
        cost_pct = st.number_input("Round-trip cost (%)", 0.0, 5.0, 0.20, 0.05)
        apply_stcg = st.checkbox("Apply 20% STCG on gains", value=True,
                                 help="ON by default: ignoring tax overstates the edge.")

        st.header("7 - Market regime")
        use_gate = st.checkbox("Apply market-regime gate", value=True,
                               help="On RISK-OFF days, show only stocks beating the market "
                                    "(positive relative strength) instead of a full basket of longs.")

        st.header("8 - Diversification")
        max_per_sector = st.slider("Max names per sector", 0, 10, 3,
                                   help="Caps how many stocks from one industry can enter the "
                                        "shortlist (highest-ranked kept). 0 = no cap. Prevents "
                                        "one sector's bad day from sinking the whole book.")

        with st.expander("Advanced filter thresholds"):
            p = {
                "regime": st.slider("Uptrend: % above 200-DMA", 0.0, 50.0, 15.0, 1.0),
                "atr":    st.slider("Volatility floor: ATR%", 0.0, 10.0, 3.5, 0.5),
                "roc":    st.slider("Breakout ROC(10) >", 0.0, 15.0, 3.0, 0.5),
                "volr":   st.slider("Breakout volume ratio >", 0.5, 4.0, 1.2, 0.1),
                "rsi_os": st.slider("Reversal oversold RSI <", 10.0, 45.0, 30.0, 1.0),
            }
        run = st.button("Scan market", type="primary", use_container_width=True)

    if not run and "scan" not in st.session_state:
        st.info("Pick a segment and click Scan market. Tip: for a nightly full run, schedule this "
                "after 4pm IST once you've confirmed a small run works.")
        return

    if run:
        bt_kwargs = dict(target_pct=target_pct, max_hold=int(max_hold), stop_method="ATR",
                         stop_value=stop_value, cost_pct=cost_pct, apply_stcg=apply_stcg,
                         rev_target_pct=6.0, rev_stop_value=1.5,
                         exit_mode=("Trailing" if exit_mode == "Trailing" else "Fixed target"),
                         trail_mult=trail_mult, max_stop_pct=max_stop_pct, max_atr_pct=max_atr_pct,
                         entry_mode=entry_mode, limit_pct=limit_pct, fill_days=int(fill_days),
                         lock_pct=lock_pct, cut_day=(int(cut_day) if cut_day else None),
                         cut_threshold=cut_threshold, partial_frac=0.0, partial_atr=3.0,
                         stop_anchor=stop_anchor, trail_anchor=trail_anchor)

        # --- market regime + relative-strength benchmark (fetched once) ---
        bench_name, idx_df = fetch_index(start, end)
        regime = compute_regime(idx_df)
        if not regime.get("index_ok"):
            st.warning("⚠️ Benchmark index unavailable — relative strength falls back to ABSOLUTE "
                       "momentum (not market-relative), and the index leg of the gate is skipped. "
                       "Breadth is still computed from the scanned stocks.")
        idx_ret_window = regime.get("idx_ret_window", 0.0)
        segments = fetch_segments(start, end)
        sector_map = fetch_sector_map()
        if not sector_map:
            st.warning("⚠️ Sector data unavailable (NSE unreachable) — sector caps cannot be applied "
                       "this run. All stocks will show sector UNKNOWN.")

        run_list = tickers[:max_n]
        rows, prog, status = [], st.progress(0.0), st.empty()
        for k, sym in enumerate(run_list):
            status.write(f"Scanning {sym}  ({k+1}/{len(run_list)}) ...")
            rows.append(scan_one(to_yahoo(sym), start, end, strategy, p, bt_kwargs,
                                 idx_ret_window, sector_map))
            prog.progress((k + 1) / len(run_list))
            time.sleep(0.05)
        status.empty(); prog.empty()

        # breadth from the scanned universe, then the composite verdict
        breadth = compute_breadth(rows)
        gate = composite_gate(regime, segments, breadth)

        # persist so row-clicks (which rerun the script) don't trigger a re-scan
        st.session_state["scan"] = {
            "res": pd.DataFrame(rows), "start": start, "end": end, "strategy": strategy,
            "p": p, "bt_kwargs": bt_kwargs, "yrs": yrs, "exit_mode": exit_mode,
            "trail_mult": trail_mult, "target_pct": target_pct, "min_hold": min_hold,
            "max_hold": max_hold, "stop_value": stop_value, "max_stop_pct": max_stop_pct,
            "max_atr_pct": max_atr_pct, "cost_pct": cost_pct, "apply_stcg": apply_stcg,
            "regime": regime, "bench_name": bench_name or "index n/a", "use_gate": use_gate,
            "segments": segments, "breadth": breadth, "gate": gate,
            "max_per_sector": max_per_sector,
            "entry_mode": entry_mode, "limit_pct": limit_pct, "fill_days": fill_days,
        }

    render_results()


def render_stock_backtest(row, S, key_prefix=""):
    """Full drill-down for one analyzed stock: chart + every backtest trade with all
    technical parameters at entry. `row` is a scan_one result row (needs 'yahoo'/'ticker')."""
    tick = row["ticker"]
    st.markdown(f"### 📈 {tick}  —  price, entries & outcomes")
    cc = st.columns(5)
    cc[0].metric("Last close", f"₹{row.get('entry_ref', row.get('last_close', '—'))}")
    cc[1].metric("Objective", f"₹{row.get('target_price', '—')}")
    cc[2].metric("Stop-loss", f"₹{row.get('stop_price', '—')}",
                 f"{row.get('stop_%', '')}%")
    cc[3].metric("Exp. days→objective", row.get("exp_days_to_target", "—"))
    cc[4].metric("Exp/DAY", f"{row.get('exp_per_day_%', 0)}%")

    with st.spinner(f"Building {tick} backtest…"):
        fig, trades_one = build_stock_chart(row["yahoo"], S["start"], S["end"],
                                            S["strategy"], S["p"], S["bt_kwargs"])
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}fig_{tick}")
        st.caption("Green = objective hit · light green = trailing profit · red = stop · grey = time exit. "
                   "Lower panel = cumulative net % of all historical trades.")

    if trades_one is None or trades_one.empty:
        st.info("No historical trades for this stock under the current settings.")
        return

    t = trades_one.copy()
    st.markdown(f"#### 🧾 Every backtest trade for {tick}  ({len(t)} trades)")
    wins = (t["net_return_%"] > 0).sum()
    q = st.columns(6)
    q[0].metric("Trades", len(t))
    q[1].metric("Profitable", f"{100*wins/len(t):.0f}%")
    q[2].metric("Hit objective", f"{100*(t['outcome']=='TARGET').mean():.0f}%")
    q[3].metric("Avg net / trade", f"{t['net_return_%'].mean():+.2f}%")
    q[4].metric("Best / Worst", f"{t['net_return_%'].max():+.0f}% / {t['net_return_%'].min():+.0f}%")
    q[5].metric("Avg hold", f"{t['days_held'].mean():.1f}d")

    facts = ["signal_date", "entry_date", "exit_date", "days_held", "outcome",
             "trade_type", "signal_close", "limit_price", "entry_price",
             "target_price", "stop_price", "exit_price",
             "gross_return_%", "net_return_%", "hit_target", "partial_taken", "peak_gain_%"]
    tech = [c for c in ["pct_vs_sma200", "pct_vs_sma20", "rsi14", "roc10", "atr_pct",
                        "vol_ratio", "macd_hist", "adx14", "bb_pctB", "dist_52wH",
                        "obv_slope10"] if c in t.columns]
    ordered = [c for c in facts if c in t.columns] + tech
    ordered += [c for c in t.columns if c not in ordered]
    t = t[ordered].sort_values("entry_date", ascending=False).reset_index(drop=True)
    st.dataframe(t, use_container_width=True, height=380, key=f"{key_prefix}tbl_{tick}")
    st.caption("Trade facts first (dates, entry/limit/objective/stop/exit, return, holding days, "
               "outcome), then the **technical parameters at entry** — trend (%vs 200/20-DMA, ADX), "
               "momentum (RSI, ROC, MACD), volatility (ATR%), volume ratio, Bollinger %B, distance "
               "from 52-week high, OBV slope. Exactly what the signal saw on the day it fired.")
    st.download_button(f"⬇️ Download {tick} full backtest", t.to_csv(index=False).encode(),
                       file_name=f"{tick}_backtest_trades.csv", mime="text/csv",
                       key=f"{key_prefix}dl_{tick}")
    with st.expander("What each technical column means"):
        st.markdown(
            "- **pct_vs_sma200 / sma20** — % above the 200- and 20-day moving average\n"
            "- **rsi14** — momentum oscillator (<30 oversold, >70 overbought)\n"
            "- **roc10** — 10-day rate of change\n"
            "- **macd_hist** — MACD histogram (momentum turning)\n"
            "- **adx14** — trend strength (>~25 = real trend)\n"
            "- **atr_pct** — volatility as % of price\n"
            "- **vol_ratio** — volume ÷ 20-day average\n"
            "- **bb_pctB** — position in Bollinger band (0 lower, 100 upper)\n"
            "- **dist_52wH** — % below the 52-week high\n"
            "- **obv_slope10** — accumulation vs distribution"
        )


def render_results():
    S = st.session_state.get("scan")
    if not S:
        return
    res = S["res"]
    ok = res[res["status"] == "ok"].copy()
    bad = res[res["status"] != "ok"].copy()

    # ---------- market-regime banner ----------
    regime = S.get("regime", {"status": "UNKNOWN"})
    use_gate = S.get("use_gate", True)
    bench = S.get("bench_name", "index")
    segments = S.get("segments", {})
    breadth = S.get("breadth", {"status": "UNKNOWN"})
    gate = S.get("gate", {"final": regime.get("status", "UNKNOWN"), "reasons": []})
    rstat = gate.get("final", "UNKNOWN")          # composite verdict drives the gate

    seg_txt = " · ".join(f"{s} {v['pct_vs_200']:+.1f}% vs 200-DMA" for s, v in segments.items()) \
              or "segment indices unavailable"
    br_txt = (f"breadth {breadth.get('status')} "
              f"({breadth.get('advancers','?')} adv / {breadth.get('decliners','?')} dec, "
              f"{breadth.get('pct_above_50dma','?')}% above 50-DMA)")
    idx_txt = (f"{bench} {regime.get('pct_vs_200','?')}% vs 200-DMA, 10d {regime.get('roc10','?')}%"
               if regime.get("index_ok") else f"{bench} unavailable")

    if rstat == "RISK-ON":
        st.success(f"🟢 Market: **RISK-ON** — {idx_txt} · {br_txt} · {seg_txt}. "
                   "Long setups favoured; full shortlist shown.")
    elif rstat == "NEUTRAL":
        st.warning(f"🟡 Market: **NEUTRAL** — {idx_txt} · {br_txt} · {seg_txt}. "
                   + ("Gate ON: list trimmed to relative-strength leaders (RS > 0)."
                      if use_gate else "Gate OFF: full list shown."))
    elif rstat == "RISK-OFF":
        veto = gate.get("breadth_veto")
        st.error(f"🔴 Market: **RISK-OFF** — {idx_txt} · {br_txt} · {seg_txt}. "
                 + ("⚠️ **Breadth veto**: the headline index is green but the broad market is falling — "
                    "exactly the trap that sinks a basket of longs. " if veto else "")
                 + ("Gate ON: only stocks beating the market (RS > 0) are shown."
                    if use_gate else "Gate OFF: full basket of longs shown (higher risk)."))
    else:
        st.info("⚪ Market state unknown (index + breadth unavailable) — gate not applied this run.")
    if gate.get("reasons"):
        st.caption("Gate inputs → " + " | ".join(gate["reasons"]))

    # ---------- point 5: how prioritisation works ----------
    with st.expander("❓ How are stocks prioritised?  (ranking logic)", expanded=False):
        st.markdown(
            "Candidates are ranked by a **blended score = confidence × relative-strength tilt**:\n\n"
            "**confidence = max(expectancy, 0) × win-rate × sample-size-damping × 10** — the historical edge.\n\n"
            "**relative strength (RS%)** = the stock's return minus the index's over ~3 months. "
            "RS > 0 means it's *beating the market*. The blend nudges market-beating stocks up and "
            "laggards down (bounded ±50%), so on weak days the leaders rise to the top.\n\n"
            "**Market-regime gate (composite):** three inputs decide RISK-ON / NEUTRAL / RISK-OFF — "
            "(1) the broad index vs its 200-DMA and 10-day momentum, (2) the **mid/small-cap segment "
            "indices** vs their own 200-DMA (your universe lives there, not in the IT mega-caps that "
            "can lift the headline), and (3) **advance/decline breadth** counted across the stocks you "
            "just scanned. Negative breadth can **veto a green index** — the exact trap where a basket "
            "of longs sinks while the Nifty prints positive. On RISK-OFF *and* NEUTRAL the gate keeps "
            "only positive-RS names. Sample-size damping still discounts thin, lucky histories.\n\n"
            "**Sector-exposure cap:** after ranking and gating, at most *N* names per industry survive "
            "(the highest-ranked ones). A shortlist of 98 stocks that are really 4–5 correlated sector "
            "bets offers *fake* diversification — one sector's bad day sinks the whole book. The cap "
            "converts that into real diversification. Sectors come from NSE's own Industry classification."
        )

    if ok.empty:
        st.warning("No stocks scanned successfully. Re-run (Yahoo can be patchy).")
    else:
        # ======= TABLE 1: TONIGHT'S INVESTMENT ANALYSIS (action) =======
        st.subheader("🎯 Tonight's Investment Analysis  —  what to do if you buy tomorrow")
        cand = ok[ok["signals_today"]].copy()
        # apply composite gate: on RISK-OFF and NEUTRAL, keep only market-beating (positive RS) names
        gate_note = ""
        if use_gate and rstat in ("RISK-OFF", "NEUTRAL") and not cand.empty:
            before = len(cand)
            cand = cand[cand["rel_strength"] > 0]
            gate_note = (f"{rstat} gate: removed {before - len(cand)} laggard(s), "
                         f"kept {len(cand)} name(s) beating the market.")
        cand = cand.sort_values("rank_score", ascending=False).reset_index(drop=True)

        # --- SECTOR-EXPOSURE CAP: keep at most N per industry (best-ranked survive) ---
        max_per_sector = S.get("max_per_sector", 3)
        pre_cap = cand.copy()
        sector_note, dropped = "", {}
        if max_per_sector > 0 and not cand.empty:
            cand, dropped = apply_sector_caps(cand, max_per_sector)
            cand = cand.reset_index(drop=True)
            if dropped:
                det = ", ".join(f"{s} (−{n})" for s, n in sorted(dropped.items(), key=lambda x: -x[1]))
                sector_note = (f"Sector cap ({max_per_sector}/sector): trimmed "
                               f"{sum(dropped.values())} correlated name(s) → {det}")

        if cand.empty:
            st.info("No qualifying candidate after the regime gate. On a risk-off day with no "
                    "market-beating setups, standing aside is the correct output — check tomorrow.")
        else:
            if gate_note:
                st.caption("🔴 " + gate_note)
            if sector_note:
                st.caption("🧩 " + sector_note)
            # concentration before vs after (shows the fake-diversification problem plainly)
            if max_per_sector > 0 and not pre_cap.empty and "sector" in pre_cap.columns:
                top_pre = pre_cap["sector"].value_counts()
                if len(top_pre) and top_pre.iloc[0] > max_per_sector:
                    st.caption(f"Concentration: before cap, **{top_pre.index[0]}** alone held "
                               f"{top_pre.iloc[0]} of {len(pre_cap)} names "
                               f"({100*top_pre.iloc[0]/len(pre_cap):.0f}%). "
                               f"After cap: {len(cand)} names across {cand['sector'].nunique()} sector(s).")
            inv = cand[["ticker", "sector", "regime_today", "rank_score", "confidence", "rel_strength",
                        "entry_ref", "plan_entry", "target_price", "stop_price", "stop_%",
                        "exp_days_to_target", "last_atr_pct", "remark"]].copy()
            _em = S.get("entry_mode", "Market open")
            _entry_label = "BUY limit ₹" if _em == "Limit" else "Entry (open)"
            inv.columns = ["Stock", "Sector", "Signal", "Rank", "Conf(/day)", "RS%", "Last close",
                           _entry_label, "Objective ₹", "Stop ₹", "Stop %", "Exp. days→objective", "ATR%", "Remark"]
            if S.get("entry_mode") == "Limit":
                st.caption(f"📥 **Place a BUY LIMIT at the 'BUY limit ₹' price** "
                           f"({S.get('limit_pct',0)}% below the signal close), valid "
                           f"{S.get('fill_days',1)} session(s). If it never fills, **skip the trade** — "
                           f"do not chase the open. Target/Stop are computed off that limit price.")
            else:
                st.caption("⚠️ Market-at-open: you accept whatever the open gives, including gap-ups. "
                           "Switch to Limit entry to avoid chasing.")
            st.caption("Ranked by blended score (confidence × relative-strength). RS% > 0 = beating the "
                       "market. Click a row for the chart. Stop ₹ respects your max-loss cap.")
            sel = st.dataframe(inv, use_container_width=True, height=340, hide_index=True,
                               on_select="rerun", selection_mode="single-row",
                               key="inv_table")
            st.download_button("⬇️ Download tonight's analysis", inv.to_csv(index=False).encode(),
                               file_name=f"investment_analysis_{dt.date.today()}.csv", mime="text/csv")

            # ---------- point 4: click a row -> chart ----------
            picked = None
            if sel and sel.get("selection", {}).get("rows"):
                picked = cand.iloc[sel["selection"]["rows"][0]]
            if picked is not None:
                render_stock_backtest(picked, S, key_prefix="inv_")

        # ======= TABLE 2: BACKTEST TRACK RECORD (evidence) =======
        st.subheader("📊 Backtest Track Record  —  historical proof behind each stock")
        bt = ok.sort_values("rank_score", ascending=False).reset_index(drop=True)
        rec = bt[["ticker", "signals_today", "rank_score", "exp_per_day_%", "rel_strength", "hist_trades", "win_%",
                  "target_hits", "target_%", "trail_exits", "trail_%", "stop_hits", "stop_hit_%",
                  "time_exits", "time_%", "time_win", "time_loss",
                  "expectancy_%", "avg_win_%", "avg_loss_%", "avg_days",
                  "bt_from", "bt_to", "years", "remark"]].copy()
        rec.columns = ["Stock", "Signals today", "Rank", "Exp/DAY%", "RS%", "Trades", "Win%",
                       "Target #", "Target %", "Trail #", "Trail %", "Stop #", "Stop %",
                       "Time #", "Time %", "Time-win", "Time-loss",
                       "Expectancy%", "Avg win%", "Avg loss%", "Avg days",
                       "BT from", "BT to", "Years", "Remark"]
        st.caption("Point 3 breakdown: Win% / Target = trades that truly hit 10%. "
                   "Trail = profitable trailing exits below 10%. Stop = losses. "
                   "Time = held to max days (split into win/loss). Profit trades = Target + Trail + Time-win.")
        st.caption("**Click any row to open that stock's full backtest** — every trade, entry/exit/"
                   "stop prices, returns, holding days, and the technical parameters at entry.")
        sel_rec = st.dataframe(rec, use_container_width=True, height=340, hide_index=True,
                               on_select="rerun", selection_mode="single-row", key="rec_table")
        if sel_rec and sel_rec.get("selection", {}).get("rows"):
            picked_rec = bt.iloc[sel_rec["selection"]["rows"][0]]
            render_stock_backtest(picked_rec, S, key_prefix="rec_")
        st.download_button("⬇️ Download backtest track record", rec.to_csv(index=False).encode(),
                           file_name=f"backtest_record_{dt.date.today()}.csv", mime="text/csv")

        c1, c2, c3 = st.columns(3)
        c1.metric("Stocks scanned OK", len(ok))
        c2.metric("Signalling today", int(ok["signals_today"].sum()))
        c3.metric("Avg expectancy (segment)", f'{ok["expectancy_%"].mean():.2f}%')

    with st.expander("📐 What the scan uses (parameters, indicators, risk)"):
        st.markdown(
            f"**Strategy:** `{S['strategy']}` - {engine.STRATEGY_HELP[S['strategy']]}\n\n"
            f"**Backtest window:** target {S['yrs']}y (per-stock actual range in the tables).\n\n"
            f"**Exit:** {S['exit_mode']} (trail {S['trail_mult']}x ATR) - Target {S['target_pct']}% - "
            f"Hold {S['min_hold']}-{S['max_hold']}d.\n\n"
            f"**Risk:** stop {S['stop_value']}x ATR, max-loss cap {S['max_stop_pct']}%, "
            f"skip if ATR% > {S['max_atr_pct']}, cost {S['cost_pct']}%"
            f"{', 20% STCG' if S['apply_stcg'] else ''}.\n\n"
            "**Indicators per stock (no look-ahead):** MAs 5/20/50/200, RSI(14), MACD(12,26,9), ATR%, "
            "Bollinger %B & bandwidth, Stochastics, OBV & slope, ADX/+-DI, volume ratio & surge, "
            "20-day breakout, 52-week distance, candle body/gap."
        )

    if not bad.empty:
        with st.expander(f"⚠️ {len(bad)} stocks skipped or failed"):
            st.dataframe(bad[["ticker", "status"]].reset_index(drop=True),
                         use_container_width=True, hide_index=True)
            st.caption("'insufficient data' = recent listing below the 1-year bar. "
                       "'fetch error/no data' = Yahoo hiccup or wrong symbol; re-run to retry.")

    st.divider()
    st.caption("Signals are historical-edge candidates, not guarantees. ~1/3 of trades hit target and "
               "some lose; size positions and honour stops. Yahoo data can be delayed/patchy. "
               "Educational tool - not investment advice.")


if __name__ == "__main__":
    main()