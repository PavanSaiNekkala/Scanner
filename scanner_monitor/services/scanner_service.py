"""
Core scanner service.

This file contains NO Streamlit code.
It only runs scans and returns results.
"""

from dataclasses import dataclass
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import scanner_monitor.swing_screener_app as engine

@dataclass
class ScanResult:
    ticker: str
    raw_data: pd.DataFrame
    returns: pd.Series 
    indicators: pd.DataFrame
    trades: pd.DataFrame
    statistics: dict[str, Any]
    summary: dict[str, Any]

@dataclass(frozen=True)
class TradePlan:
    entry_ref: float
    limit_price: float
    plan_entry: float
    stop_price: float
    stop_pct: float
    target_price: float
    days_to_target: float  
    days_to_achieve_target: str

class ScannerService:
    """
    Reusable scanner service.

    Stateless service that executes
    technical scans and returns ScanResult.
    """

    def run_scan(
        self,
        ticker: str,
        strategy: str,
        params: dict,
        bt_kwargs: dict,
        start_date: dt.date,
        end_date: dt.date,
        idx_ret_window: float = 0.0,
        sector_map: dict | None = None,
    ) -> ScanResult:

        return scan_one(
            ticker=ticker,
            start=start_date,
            end=end_date,
            strategy=strategy,
            p=params,
            bt_kwargs=bt_kwargs,
            idx_ret_window=idx_ret_window,
            sector_map=sector_map,
        )

    def run_batch(
        self,
        tickers: list[str],
        strategy: str,
        params: dict,
        bt_kwargs: dict,
        start_date: dt.date,
        end_date: dt.date,
        idx_ret_window: float = 0.0,
        sector_map: dict | None = None,
        max_workers: int = 8,
    ) -> list[ScanResult]:

        results: list[ScanResult] = []

        with ThreadPoolExecutor(
            max_workers=max_workers,
        ) as executor:

            futures = {
                executor.submit(
                    self.run_scan,
                    ticker=ticker,
                    strategy=strategy,
                    params=params,
                    bt_kwargs=bt_kwargs,
                    start_date=start_date,
                    end_date=end_date,
                    idx_ret_window=idx_ret_window,
                    sector_map=sector_map,
                ): ticker
                for ticker in tickers
            }

            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    results.append(
                        future.result()
                    )
                except Exception as e:
                    print(
                        f"FAILED {ticker}: {e}"
                    )
        return results
    
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
    "MidCap": [
        "^NSEMDCP50",
        "NIFTY_MIDCAP_100.NS",
        "^CNXMIDCAP",
    ],
    "SmallCap": [
        "NIFTYSMLCAP250.NS",
        "^CNXSMCAP",
    ],
}


def normalize_yahoo_symbol(
    ticker: str,
) -> str:
    """
    Convert NSE symbols into Yahoo Finance format.
    """
    ticker = ticker.strip().upper()
    if not ticker.startswith("^") and not ticker.endswith(".NS"):
        ticker = f"{ticker}.NS"
    return ticker

def fetch_one(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:

    ticker = normalize_yahoo_symbol(ticker)
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)

    return df.dropna()


def fetch_index(start: dt.date, end: dt.date):
    """
    Fetch a broad benchmark index
    (Nifty 500, fallback Nifty 50)
    for regime + RS.
    """

    if yf is None:
        return None, pd.DataFrame()

    for t in BENCH_TICKERS:
        try:
            df = yf.Ticker(t).history(
                start=start,
                end=end,
                interval="1d",
                auto_adjust=True,
            )

            if df is not None and not df.empty:
                df = df[
                    ["Open", "High", "Low", "Close", "Volume"]
                ].copy()

                df.index = pd.to_datetime(df.index).tz_localize(None)

                return t, df.dropna()

        except Exception:
            continue

    return None, pd.DataFrame()



def fetch_segments(start: dt.date, end: dt.date) -> dict:
    """
    Fetch mid/small-cap segment indices.

    Returns:
        {segment_name: pct_vs_200dma}
    """

    out = {}

    if yf is None:
        return out

    for seg, candidates in SEGMENT_TICKERS.items():
        for t in candidates:
            try:
                df = yf.Ticker(t).history(
                    start=start,
                    end=end,
                    interval="1d",
                    auto_adjust=True,
                )

                if df is None or df.empty or len(df) < 210:
                    continue

                c = df["Close"].dropna()
                s200 = c.rolling(200).mean().iloc[-1]

                if not np.isfinite(s200):
                    continue

                out[seg] = {
                    "ticker": t,
                    "pct_vs_200": round(
                        float(c.iloc[-1] / s200 - 1) * 100,
                        2,
                    ),
                    "above_200": bool(c.iloc[-1] > s200),
                }

                break

            except Exception:
                continue

    return out


def compute_breadth(rows: list) -> dict:
    """
    Advance/decline breadth computed from the scanned universe itself
    (no extra fetches).

    This catches narrow, breadth-negative days hidden behind
    a green headline index.
    """

    ok = [
        r
        for r in rows
        if r.get("status") == "ok"
        and np.isfinite(r.get("day_chg_%", np.nan))
    ]

    n = len(ok)

    if n == 0:
        return {
            "status": "UNKNOWN",
            "n": 0,
        }

    adv = sum(1 for r in ok if r["day_chg_%"] > 0)
    dec = sum(1 for r in ok if r["day_chg_%"] < 0)
    above50 = sum(1 for r in ok if r.get("above_50dma"))

    ad_ratio = adv / max(dec, 1)
    pct_adv = 100 * adv / n
    pct_above50 = 100 * above50 / n

    if pct_adv >= 55 and pct_above50 >= 50:
        status = "POSITIVE"
    elif pct_adv < 40 or pct_above50 < 40:
        status = "NEGATIVE"
    else:
        status = "MIXED"

    return {
        "status": status,
        "n": n,
        "advancers": adv,
        "decliners": dec,
        "pct_advancers": round(pct_adv, 1),
        "pct_above_50dma": round(pct_above50, 1),
        "ad_ratio": round(ad_ratio, 2),
    }



def compute_regime(idx_df: pd.DataFrame) -> dict:
    """
    Trend/momentum of the broad benchmark.
    """

    if idx_df.empty or len(idx_df) < 210:
        return {
            "status": "UNKNOWN",
            "note": "index data unavailable",
            "idx_ret_window": 0.0,
            "index_ok": False,
        }

    c = idx_df["Close"]

    s200 = c.rolling(200).mean().iloc[-1]
    last = float(c.iloc[-1])

    above200 = bool(last > s200) if np.isfinite(s200) else True
    pct_vs200 = (last / s200 - 1) * 100 if np.isfinite(s200) else np.nan

    roc10 = (
        (c.iloc[-1] / c.iloc[-11] - 1) * 100
        if len(c) > 11
        else 0.0
    )

    idx_ret_window = (
        (c.iloc[-1] / c.iloc[-(RS_WINDOW + 1)] - 1) * 100
        if len(c) > RS_WINDOW
        else 0.0
    )

    if above200 and roc10 > -1.0:
        status = "RISK-ON"
    elif above200 or roc10 > -3.0:
        status = "NEUTRAL"
    else:
        status = "RISK-OFF"

    return {
        "status": status,
        "above_200": above200,
        "pct_vs_200": round(float(pct_vs200), 2),
        "roc10": round(float(roc10), 2),
        "idx_ret_window": float(idx_ret_window),
        "last": round(last, 2),
        "index_ok": True,
    }



def composite_gate(regime: dict, segments: dict, breadth: dict) -> dict:
    """
    Combine index trend + segment trend + breadth
    into one market verdict.
    """

    idx_state = regime.get("status", "UNKNOWN")
    br = breadth.get("status", "UNKNOWN")

    seg_below = [
        s
        for s, v in segments.items()
        if not v.get("above_200", True)
    ]

    score = 0

    if idx_state == "RISK-ON":
        score += 1
    elif idx_state == "RISK-OFF":
        score -= 1

    if br == "POSITIVE":
        score += 1
    elif br == "NEGATIVE":
        score -= 1

    if seg_below:
        score -= 1

    if br == "NEGATIVE" and idx_state != "RISK-ON":
        final = "RISK-OFF"
    elif score >= 2:
        final = "RISK-ON"
    elif score <= -1:
        final = "RISK-OFF"
    else:
        final = "NEUTRAL"

    reasons = [
        f"index {idx_state}",
        f"breadth {br}",
    ]

    if seg_below:
        reasons.append(f"{'/'.join(seg_below)} below 200-DMA")
    elif segments:
        reasons.append("segments above 200-DMA")

    return {
        "final": final,
        "score": score,
        "reasons": reasons,
        "breadth_veto": (
            br == "NEGATIVE"
            and idx_state == "RISK-ON"
        ),
    }



def _validate_market_data(
    ticker: str,
    start: dt.date,
    end: dt.date,
) -> pd.DataFrame:
    """
    Fetch and validate market data.
    """

    try:
        raw = fetch_one(
            ticker,
            start,
            end,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch data for {ticker}"
        ) from e

    if raw.empty:
        raise ValueError(
            f"No market data found for {ticker}"
        )

    if len(raw) < MIN_DAYS:
        raise ValueError(
            f"{ticker} has only {len(raw)} trading days "
            f"(minimum required: {MIN_DAYS})"
        )

    return raw



def _run_strategy(
    raw: pd.DataFrame,
    strategy: str,
    params: dict,
    bt_kwargs: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Run indicator generation,
    signal generation,
    backtest,
    and statistics.
    """

    df = engine.compute_indicators(raw)

    df = engine.generate_signals(
        df,
        strategy,
        params,
    )

    trades = engine.run_backtest(
        df,
        **bt_kwargs,
    )

    stats = engine.summarize(trades)

    return df, trades, stats



def _compute_confidence(
    stats: dict,
) -> float:

    n = stats.get("trades", 0)

    winr = stats.get(
        "profitable_%",
        0.0,
    )

    exp_day = stats.get(
        "exp_per_day_%",
        0.0,
    )

    size_factor = n / (n + 30.0)

    return round(
        max(exp_day, 0)
        * (winr / 100.0)
        * size_factor
        * 100,
        2,
    )



def _compute_rank_score(
    df: pd.DataFrame,
    stats: dict,
    confidence: float,
    idx_ret_window: float,
) -> tuple[float, float, pd.Series]:
    """
    Compute institutional rank score.

    Returns
    -------
    (
        relative_strength,
        rank_score,
        close_series,
    )
    """

    c_ser = df["Close"]

    # =====================================================
    # Relative Strength
    # =====================================================

    if len(c_ser) > RS_WINDOW:

        stock_ret_window = (
            c_ser.iloc[-1]
            / c_ser.iloc[-(RS_WINDOW + 1)]
            - 1
        ) * 100

    else:

        stock_ret_window = (
            c_ser.iloc[-1]
            / c_ser.iloc[0]
            - 1
        ) * 100

    rel_strength = round(
        float(
            stock_ret_window
            - idx_ret_window
        ),
        2,
    )

    # =====================================================
    # Read Historical Metrics
    # =====================================================

    expectancy = stats.get(
        "expectancy_%",
        0.0,
    )

    profit_factor = stats.get(
        "profit_factor",
        1.0,
    )

    reward_risk = stats.get(
        "reward_risk_ratio",
        0.0,
    )

    win_rate = stats.get(
        "profitable_%",
        0.0,
    )

    trades = stats.get(
        "trades",
        0,
    )

    recovery = stats.get(
        "recovery_factor",
        0.0,
    )

    max_dd = abs(
        stats.get(
            "max_drawdown_%",
            0.0,
        )
    )

    above_200 = bool(
        df["Close"].iloc[-1]
        > df["sma200"].iloc[-1]
    )

    # =====================================================
    # Normalize Scores (0-1)
    # =====================================================

    expectancy_score = np.clip(
        expectancy / 5.0,
        0,
        1,
    )

    pf_score = np.clip(
        (profit_factor - 1.0) / 2.0,
        0,
        1,
    )

    rr_score = np.clip(
        reward_risk / 3.0,
        0,
        1,
    )

    win_score = np.clip(
        win_rate / 70.0,
        0,
        1,
    )

    rs_score = np.clip(
        (rel_strength + 20) / 40,
        0,
        1,
    )

    conf_score = np.clip(
        confidence / 10.0,
        0,
        1,
    )

    trade_score = np.clip(
        trades / 100.0,
        0,
        1,
    )

    recovery_score = np.clip(
        recovery / 5.0,
        0,
        1,
    )

    dd_score = np.clip(
        1 - max_dd / 50.0,
        0,
        1,
    )

    trend_score = (
        1.0
        if above_200
        else 0.0
    )

    # =====================================================
    # Institutional Composite Score
    # =====================================================

    rank_score = (
        expectancy_score * 20
        + pf_score * 15
        + rr_score * 10
        + win_score * 10
        + rs_score * 15
        + conf_score * 10
        + trade_score * 5
        + recovery_score * 10
        + dd_score * 5
        + trend_score * 5
    )

    rank_score = round(
        rank_score,
        2,
    )

    return (
        rel_strength,
        rank_score,
        c_ser,
    )



def _compute_trade_levels(
    last: pd.Series,
    stats: dict,
    bt_kwargs: dict,
) -> TradePlan:

    entry_ref = float(last["Close"])

    atr_now = (
        float(last["atr14"])
        if np.isfinite(last["atr14"])
        else 0.0
    )

    stop_mult = bt_kwargs.get(
        "stop_value",
        2.0,
    )

    max_stop_pct = (
        bt_kwargs.get(
            "max_stop_pct",
            8.0,
        )
        or 8.0
    )

    reward_multiple = bt_kwargs.get(
        "reward_multiple",
        2.0,
    )

    entry_mode = bt_kwargs.get(
        "entry_mode",
        "Market open",
    )

    limit_pct = bt_kwargs.get(
        "limit_pct",
        0.0,
    )

    if entry_mode == "Limit":

        limit_price = round(
            entry_ref * (1 - limit_pct / 100),
            2,
        )

        plan_entry = limit_price

    else:

        limit_price = np.nan
        plan_entry = entry_ref

    # =====================================================
    # Stop Loss
    # =====================================================

    stop_price = plan_entry - stop_mult * atr_now

    floor = plan_entry * (
        1 - max_stop_pct / 100
    )

    stop_price = max(
        stop_price,
        floor,
    )

    stop_pct = round(
        (stop_price / plan_entry - 1) * 100,
        2,
    )

    # =====================================================
    # Dynamic Target
    # =====================================================

    risk_points = max(
        plan_entry - stop_price,
        atr_now,
    )

    atr_target = (
        plan_entry
        + 3.0 * atr_now
    )

    rr_target = (
        plan_entry
        + reward_multiple * risk_points
    )

    target_price = round(
        max(
            atr_target,
            rr_target,
        ),
        2,
    )
    
    med_days = stats.get(
        "med_days_to_target",
        np.nan,
    )

    n_win = stats.get(
        "n_winners",
        0,
    )

    if np.isnan(med_days):

        days_numeric = np.nan
        days_display = "n/a"

    elif n_win < 5:

        days_numeric = float(med_days)
        days_display = f"{med_days:.0f}d ⚠ thin"

    else:

        days_numeric = float(med_days)
        days_display = f"{med_days:.0f}d"

    return TradePlan(
        entry_ref=entry_ref,
        limit_price=limit_price,
        plan_entry=plan_entry,
        stop_price=stop_price,
        stop_pct=stop_pct,
        target_price=target_price,
        days_to_target=days_numeric,
        days_to_achieve_target=days_display,
    )


def _build_metadata(
    *,
    symbol: str,
    ticker: str,
    raw: pd.DataFrame,
    scan_date,
    signal_date,
    yrs: float,
) -> dict:
    """
    Build metadata section.
    """

    return {

        "ticker": symbol,
        "yahoo": ticker,
        "status": "ok",
        "scan_date": scan_date,
        "signal_date": signal_date,
        "bt_from": raw.index[0].date(),
        "bt_to": raw.index[-1].date(),
        "years": round(
            yrs,
            1,
        ),

    }


def _build_identification(
    *,
    sector: str,
) -> dict:
    """
    Build asset identification section.
    """

    return {
        "sector": sector,
        "company": "",
        "exchange": "NSE",
        "subsector": "",
    }


def _build_scanner(
    *,
    strategy: str,
    signals_today: bool,
    confidence: float,
    rank_score: float,
    regime_today: str,
) -> dict:
    """
    Build scanner metadata.
    """

    return {

        "strategy": strategy,
        "recommendation": (
            "BUY"
            if signals_today
            else "WATCH"
        ),
        "trade_status": (
            "NEW"
            if signals_today
            else "WATCH"
        ),

        "signals_today": signals_today,
        "confidence": confidence,
        "rank_score": rank_score,
        "portfolio_rank": np.nan,
        "regime_today": regime_today,

    }


def _build_market(
    *,
    last: pd.Series,
    rel_strength: float,
    c_ser: pd.Series,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    cmp: float,
    last_close: float,
    volume: int,
    avg20_volume: int,
    volume_ratio: float,
    candle_range: float,
    candle_range_pct: float,
    atr: float,
    atr_pct: float,
    above_50dma: bool,
    above_200dma: bool,
    pct_from_20dma: float,
    pct_from_50dma: float,
    pct_from_200dma: float,
) -> dict:
    """
    Build market and technical metrics.
    """

    if len(c_ser) > 1:

        day_change_pct = round(
            (
                c_ser.iloc[-1]
                / c_ser.iloc[-2]
                - 1
            ) * 100,
            2,
        )

        gap_pct = round(
            (
                last["Open"]
                / c_ser.iloc[-2]
                - 1
            ) * 100,
            2,
        )

    else:

        day_change_pct = np.nan
        gap_pct = np.nan

    return {

        # =====================================================
        # Market Data
        # =====================================================

        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
        "cmp": cmp,
        "volume": volume,
        "avg20_volume": avg20_volume,
        "volume_ratio": volume_ratio,

        # =====================================================
        # Price Action
        # =====================================================

        "day_chg_%": day_change_pct,
        "gap_%": gap_pct,
        "candle_range": candle_range,
        "candle_range_%": candle_range_pct,

        # =====================================================
        # Technical Indicators
        # =====================================================

        "atr": atr,
        "atr_points": atr,
        "atr_pct": atr_pct,
        "above_50dma": above_50dma,
        "above_200dma": above_200dma,
        "pct_from_20dma": pct_from_20dma,
        "pct_from_50dma": pct_from_50dma,
        "pct_from_200dma": pct_from_200dma,
        "rsi": (
            round(float(last["rsi14"]), 2)
            if "rsi14" in last.index
            and pd.notna(last["rsi14"])
            else np.nan
        ),
        "roc": (
            round(float(last["roc10"]), 2)
            if "roc10" in last.index
            and pd.notna(last["roc10"])
            else np.nan
        ),

        # =====================================================
        # Relative Strength
        # =====================================================

        "relative_strength": rel_strength,

    }


def _build_trade(
    *,
    trade: TradePlan,
    stats: dict,
    entry_price: float,
    target_price: float,
    stop_price: float,
    last_close: float,
    stop_pct: float,
    reward_points: float,
    risk_points: float,
    risk_pct: float,
    target_return_pct: float,
) -> dict:
    """
    Build trade setup and historical trade statistics.
    """

    return {
        # =====================================================
        # Trade Setup
        # =====================================================

        "entry": entry_price,
        "target": target_price,
        "stop_loss": stop_price,
        "entry_ref": trade.entry_ref,
        "limit_price": trade.limit_price,
        "target_hold_days": trade.days_to_target,

        # =====================================================
        # Expected Return
        # =====================================================

        "expected_return_pct": target_return_pct,
        "expected_return_points": reward_points,

        # =====================================================
        # Risk
        # =====================================================

        "risk_pct": risk_pct,
        "risk_points": risk_points,
        "risk_reward": stats.get(
            "reward_risk_ratio",
            np.nan,
        ),

        # =====================================================
        # Exit Statistics
        # =====================================================

        "target_hits": stats.get(
            "target_hits",
            0,
        ),

        "target_hit_pct": stats.get(
            "target_pct_of_all",
            0.0,
        ),

        "stop_hits": stats.get(
            "stop_hits",
            0,
        ),

        "stop_hit_pct": stats.get(
            "stop_pct_of_all",
            0.0,
        ),

        "trail_exits": stats.get(
            "trail_exits",
            0,
        ),

        "trail_pct": stats.get(
            "trail_pct_of_all",
            0.0,
        ),

        "time_exits": stats.get(
            "time_exits",
            0,
        ),

        "time_pct": stats.get(
            "time_pct_of_all",
            0.0,
        ),

        "time_win": stats.get(
            "time_win",
            0,
        ),

        "time_loss": stats.get(
            "time_loss",
            0,
        ),
    }


def _build_performance(
    *,
    stats: dict,
    remark: str,
) -> dict:
    """
    Build historical performance,
    risk metrics,
    and scanner remarks.
    """

    return {
        # =====================================================
        # Historical Performance
        # =====================================================

        "hist_trades": stats.get(
            "trades",
            0,
        ),

        "win_rate": stats.get(
            "profitable_%",
            0.0,
        ),

        "expectancy": stats.get(
            "expectancy_%",
            0.0,
        ),

        "avg_win_%": stats.get(
            "avg_win_%",
            0.0,
        ),

        "avg_loss_%": stats.get(
            "avg_loss_%",
            0.0,
        ),

        "avg_days": stats.get(
            "avg_days",
            0.0,
        ),

        "exp_per_day_%": stats.get(
            "exp_per_day_%",
            0.0,
        ),

        # =====================================================
        # Performance Metrics
        # =====================================================

        "total_return_sum_%": stats.get(
            "total_return_sum_%",
            np.nan,
        ),

        "cagr_%": stats.get(
            "cagr_%",
            np.nan,
        ),

        "profit_factor": stats.get(
            "profit_factor",
            np.nan,
        ),

        "reward_risk_ratio": stats.get(
            "reward_risk_ratio",
            np.nan,
        ),

        "recovery_factor": stats.get(
            "recovery_factor",
            np.nan,
        ),

        # =====================================================
        # Risk Metrics
        # =====================================================

        "max_drawdown_%": stats.get(
            "max_drawdown_%",
            np.nan,
        ),

        "max_consecutive_losses": stats.get(
            "max_consecutive_losses",
            np.nan,
        ),

        "seq_trades": stats.get(
            "seq_trades",
            np.nan,
        ),

        # =====================================================
        # Exit Analysis
        # =====================================================

        "cut_exits": stats.get(
            "cut_exits",
            0,
        ),

        "trail_exits": stats.get(
            "trail_exits",
            0,
        ),

        # =====================================================
        # Scanner Remarks
        # =====================================================

        "remarks": remark,
    }


def _build_summary(
    *,
    strategy: str,
    ticker: str,
    sector_map: dict | None,
    raw: pd.DataFrame,
    last: pd.Series,
    stats: dict,
    confidence: float,
    rel_strength: float,
    rank_score: float,
    c_ser: pd.Series,
    trade: TradePlan,
    signals_today: bool,
    regime_today: str,
    yrs: float,
    remark: str,
) -> dict:
    """
    Build the final scanner output dictionary.
    """
    # =====================================================
    # Identification
    # =====================================================

    symbol = (
        ticker.replace(".NS", "")
        .replace(".BO", "")
    )

    sector = (
        (sector_map or {})
        .get(
            symbol.upper(),
            "UNKNOWN",
        )
    )

    # =====================================================
    # Dates
    # =====================================================

    scan_date = raw.index[-1].date()

    signal_date = (
        scan_date
        if signals_today
        else None
    )

    # =====================================================
    # Market Prices
    # =====================================================

    open_price = round(
        float(last["Open"]),
        2,
    )

    high_price = round(
        float(last["High"]),
        2,
    )

    low_price = round(
        float(last["Low"]),
        2,
    )

    close_price = round(
        float(last["Close"]),
        2,
    )

    cmp = close_price

    volume = int(
        last["Volume"]
    )

    # =====================================================
    # Volume Statistics
    # =====================================================

    avg20_volume = int(
        raw["Volume"]
        .tail(20)
        .mean()
    )

    volume_ratio = round(
        volume / avg20_volume,
        2,
    )

    # =====================================================
    # Candle Statistics
    # =====================================================

    candle_range = round(
        high_price - low_price,
        2,
    )

    candle_range_pct = round(
        candle_range
        / close_price
        * 100,
        2,
    )

    # =====================================================
    # Trade Levels
    # =====================================================

    entry_price = round(
        trade.plan_entry,
        2,
    )

    target_price = round(
        trade.target_price,
        2,
    )

    stop_price = round(
        trade.stop_price,
        2,
    )

    last_close = round(
        trade.entry_ref,
        2,
    )

    stop_pct = trade.stop_pct

    risk_points = round(
        entry_price
        - stop_price,
        2,
    )

    reward_points = round(
        target_price
        - entry_price,
        2,
    )

    target_return_pct = round(
        reward_points
        / entry_price
        * 100,
        2,
    )

    risk_pct = round(
        risk_points
        / entry_price
        * 100,
        2,
    )

    # =====================================================
    # Technical Indicators
    # =====================================================

    atr = round(
        float(last["atr14"]),
        2,
    )

    atr_pct = round(
        float(last["atr_pct"]),
        2,
    )

    above_50dma = (
        bool(
            last["Close"]
            > last["sma50"]
        )
        if np.isfinite(
            last["sma50"]
        )
        else False
    )

    above_200dma = (
        bool(
            last["Close"]
            > last["sma200"]
        )
        if np.isfinite(
            last["sma200"]
        )
        else False
    )

    pct_from_20dma = round(
        (
            last["Close"]
            / last["sma20"]
            - 1
        )
        * 100,
        2,
    )

    pct_from_50dma = round(
        (
            last["Close"]
            / last["sma50"]
            - 1
        )
        * 100,
        2,
    )

    pct_from_200dma = round(
        (
            last["Close"]
            / last["sma200"]
            - 1
        )
        * 100,
        2,
    )

    # =====================================================
    # Price Behaviour
    # =====================================================

    if len(c_ser) > 1:

        day_change_pct = round(
            (
                c_ser.iloc[-1]
                / c_ser.iloc[-2]
                - 1
            )
            * 100,
            2,
        )

        gap_pct = round(
            (
                last["Open"]
                / c_ser.iloc[-2]
                - 1
            )
            * 100,
            2,
        )

    else:

        day_change_pct = np.nan
        gap_pct = np.nan

    metadata = _build_metadata(
        symbol=symbol,
        ticker=ticker,
        raw=raw,
        scan_date=scan_date,
        signal_date=signal_date,
        yrs=yrs,
    )

    identification = _build_identification(
        sector=sector,
    )

    scanner = _build_scanner(
        strategy=strategy,
        signals_today=signals_today,
        confidence=confidence,
        rank_score=rank_score,
        regime_today=regime_today,
    )

    market = _build_market(
        last=last,
        rel_strength=rel_strength,
        c_ser=c_ser,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        cmp=cmp,
        last_close=last_close,
        volume=volume,
        avg20_volume=avg20_volume,
        volume_ratio=volume_ratio,
        candle_range=candle_range,
        candle_range_pct=candle_range_pct,
        atr=atr,
        atr_pct=atr_pct,
        above_50dma=above_50dma,
        above_200dma=above_200dma,
        pct_from_20dma=pct_from_20dma,
        pct_from_50dma=pct_from_50dma,
        pct_from_200dma=pct_from_200dma,
    )

    trade_summary = _build_trade(
        trade=trade,
        stats=stats,
        entry_price=entry_price,
        target_price=target_price,
        stop_price=stop_price,
        last_close=last_close,
        stop_pct=stop_pct,
        reward_points=reward_points,
        risk_points=risk_points,
        risk_pct=risk_pct,
        target_return_pct=target_return_pct,
    )

    performance = _build_performance(
        stats=stats,
        remark=remark,
    )

    summary = {}

    summary.update(metadata)
    summary.update(identification)
    summary.update(scanner)
    summary.update(market)
    summary.update(trade_summary)
    summary.update(performance)

    return summary



def scan_one(
    ticker,
    start,
    end,
    strategy,
    p,
    bt_kwargs,
    idx_ret_window=0.0,
    sector_map=None,
) -> ScanResult:

    raw = _validate_market_data(
        ticker,
        start,
        end,
    )

    # ---------------------------------------------------------
    # Daily Return Series
    # ---------------------------------------------------------

    returns = (
        raw["Close"]
        .pct_change()
        .dropna()
        .rename(ticker)
    )

    df, trades, stats = _run_strategy(
        raw,
        strategy,
        p,
        bt_kwargs,
    )

    yrs = (raw.index[-1] - raw.index[0]).days / 365.25

    remark = (
        ""
        if yrs >= TARGET_YEARS - 0.5
        else f"limited history: {yrs:.1f}y (<{TARGET_YEARS}y) - lower confidence"
    )

    last = df.iloc[-1]

    signals_today = bool(last["signal"])
    regime_today = (
        last.get("trade_type", "") or "UPTREND"
        if signals_today
        else ""
    )

    confidence = _compute_confidence(stats)

    rel_strength, rank_score, c_ser = (
        _compute_rank_score(
            df=df,
            stats=stats,
            confidence=confidence,
            idx_ret_window=idx_ret_window,
        )
    )

    trade = _compute_trade_levels(
        last,
        stats,
        bt_kwargs,
    )

    summary = _build_summary(
        strategy=strategy,
        ticker=ticker,
        sector_map=sector_map,
        raw=raw,
        last=last,
        stats=stats,
        confidence=confidence,
        rel_strength=rel_strength,
        rank_score=rank_score,
        c_ser=c_ser,
        trade=trade,
        signals_today=signals_today,
        regime_today=regime_today,
        yrs=yrs,
        remark=remark,
    )

    return ScanResult(
        ticker=ticker,
        raw_data=raw,
        returns=returns,
        indicators=df,
        trades=trades,
        statistics=stats,
        summary=summary,
    )



_SERVICE = ScannerService()


def run_scan(
    ticker: str,
    strategy: str,
    params: dict,
    bt_kwargs: dict,
    start_date,
    end_date,
    idx_ret_window: float = 0.0,
    sector_map: dict | None = None,
) -> ScanResult:

    return _SERVICE.run_scan(
        ticker=ticker,
        strategy=strategy,
        params=params,
        bt_kwargs=bt_kwargs,
        start_date=start_date,
        end_date=end_date,
        idx_ret_window=idx_ret_window,
        sector_map=sector_map,
    )

def run_batch(
    tickers: list[str],
    strategy: str,
    params: dict,
    bt_kwargs: dict,
    start_date,
    end_date,
    idx_ret_window: float = 0.0,
    sector_map: dict | None = None,
    max_workers: int = 8,
) -> list[ScanResult]:

    return _SERVICE.run_batch(
        tickers=tickers,
        strategy=strategy,
        params=params,
        bt_kwargs=bt_kwargs,
        start_date=start_date,
        end_date=end_date,
        idx_ret_window=idx_ret_window,
        sector_map=sector_map,
        max_workers=max_workers,
    )
