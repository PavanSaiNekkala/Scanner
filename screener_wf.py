"""
NSE Swing-Trade Screener & Backtester
=====================================
An interactive Streamlit app that reproduces the full analysis pipeline built in our
research chat: it pulls a stock from Yahoo Finance, computes ~38 technical indicators
(no look-ahead), applies one of three filter strategies (PASS_recommended / PASS_tight /
PASS_balanced), and backtests a swing strategy using the triple-barrier method
(take-profit / stop-loss / time-stop).

Run with:  streamlit run swing_screener_app.py
"""

import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import yfinance as yf
except Exception:
    yf = None


# ======================================================================================
#  1. DATA
# ======================================================================================
@st.cache_data(show_spinner=False)
def fetch_data(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    """Download daily OHLCV from Yahoo Finance (auto-adjusted for splits/bonus)."""
    if yf is None:
        raise RuntimeError("yfinance is not installed.")
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df.dropna()
    return df


# ======================================================================================
#  2. INDICATORS  (identical logic to the research pipeline; strictly no look-ahead)
# ======================================================================================
def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def _sma(s, n):
    return s.rolling(n).mean()


def _rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()  # Wilder's smoothing


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c, v = df["Open"], df["High"], df["Low"], df["Close"], df["Volume"]

    # --- Trend / moving averages ---
    for n in (5, 10, 20, 50, 200):
        df[f"sma{n}"] = _sma(c, n)
    df["ema20"], df["ema50"] = _ema(c, 20), _ema(c, 50)
    df["pct_vs_sma20"] = (c / df["sma20"] - 1) * 100
    df["pct_vs_sma50"] = (c / df["sma50"] - 1) * 100
    df["pct_vs_sma200"] = (c / df["sma200"] - 1) * 100
    df["ma_aligned_up"] = (
        (df["sma5"] > df["sma20"]) & (df["sma20"] > df["sma50"])
    ).astype(int)

    # --- RSI(14) ---
    delta = c.diff()
    gain = _rma(delta.clip(lower=0), 14)
    loss = _rma(-delta.clip(upper=0), 14)
    rs = gain / loss.replace(0, np.nan)
    df["rsi14"] = 100 - 100 / (1 + rs)

    # --- Rate of change ---
    df["roc5"] = (c / c.shift(5) - 1) * 100
    df["roc10"] = (c / c.shift(10) - 1) * 100

    # --- MACD(12,26,9) ---
    macd = _ema(c, 12) - _ema(c, 26)
    sig = _ema(macd, 9)
    df["macd"], df["macd_signal"], df["macd_hist"] = macd, sig, macd - sig
    df["macd_bull"] = (macd > sig).astype(int)

    # --- ATR(14) & ATR% ---
    tr = pd.concat([(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(
        axis=1
    )
    df["atr14"] = _rma(tr, 14)
    df["atr_pct"] = df["atr14"] / c * 100

    # --- Bollinger(20,2) ---
    mid = _sma(c, 20)
    sd = c.rolling(20).std()
    upper, lower = mid + 2 * sd, mid - 2 * sd
    df["bb_pctB"] = (c - lower) / (upper - lower) * 100
    df["bb_bandwidth"] = (upper - lower) / mid * 100

    # --- Stochastic(14,3) ---
    ll, hh = l.rolling(14).min(), h.rolling(14).max()
    k = (c - ll) / (hh - ll) * 100
    df["stoch_k"], df["stoch_d"] = k, k.rolling(3).mean()

    # --- Volume ---
    df["vol_sma20"] = _sma(v, 20)
    df["vol_ratio"] = v / df["vol_sma20"]
    df["vol_surge"] = (df["vol_ratio"] >= 1.5).astype(int)
    obv = (np.sign(c.diff()).fillna(0) * v).cumsum()
    df["obv"] = obv
    df["obv_slope10"] = obv.diff(10)

    # --- Breakout / range position ---
    df["high20"] = h.rolling(20).max().shift(1)
    df["breakout20"] = (c > df["high20"]).astype(int)
    hi52 = h.rolling(252).max()
    lo52 = l.rolling(252).min()
    df["dist_52wH"] = (c / hi52 - 1) * 100
    df["dist_52wL"] = (c / lo52 - 1) * 100
    rng14 = h.rolling(14).max() - l.rolling(14).min()
    df["pos_in_range14"] = (c - l.rolling(14).min()) / rng14 * 100

    # --- Candle / price action ---
    df["gap_up"] = (o - c.shift()) / c.shift() * 100
    df["body_pct"] = (c - o) / o * 100
    df["up_day"] = (c > c.shift()).astype(int)

    # --- ADX(14) ---
    up = h.diff()
    dn = -l.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr = _rma(tr, 14)
    plus_di = 100 * _rma(pd.Series(plus_dm, index=c.index), 14) / atr
    minus_di = 100 * _rma(pd.Series(minus_dm, index=c.index), 14) / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["adx14"], df["plus_di"], df["minus_di"] = _rma(dx, 14), plus_di, minus_di

    return df


# ======================================================================================
#  3. SIGNALS  (the three strategies from our analysis)
# ======================================================================================
def generate_signals(
    df: pd.DataFrame,
    strategy: str,
    p: dict,
    bench_close: pd.Series = None,
    require_rs: bool = False,
    rs_window: int = 63,
) -> pd.DataFrame:
    """If `bench_close` is supplied, a rolling relative-strength series is computed
    (stock return minus index return over `rs_window`). With require_rs=True, signals
    only fire when the stock is OUTPERFORMING the index — i.e. it can rise even while
    the market falls. This makes the RS filter *backtestable*, not just a live-scan tilt.
    """
    df = df.copy()
    c, o = df["Close"], df["Open"]

    # --- rolling relative strength vs the benchmark (no look-ahead: all trailing) ---
    if bench_close is not None:
        b = bench_close.reindex(df.index).ffill()
        stock_ret = c / c.shift(rs_window) - 1
        bench_ret = b / b.shift(rs_window) - 1
        df["rs_roll"] = (stock_ret - bench_ret) * 100
    else:
        df["rs_roll"] = np.nan
    regime = df["pct_vs_sma200"] > p["regime"]  # strong uptrend
    obv_rise = df["obv_slope10"] > 0  # accumulation
    vol_ok = df["atr_pct"] > p["atr"]  # enough volatility

    A = regime & obv_rise  # momentum-continuation branch
    B = (
        (df["pct_vs_sma20"] > 0)
        & (df["roc10"] > p["roc"])
        & (df["vol_ratio"] > p["volr"])
    )  # breakout branch

    # ---- COUNTER-TREND / REVERSAL branch (fires BELOW the 200-DMA) ----
    # Never a naked "buy the dip": every condition demands PROOF the fall is pausing.
    rsi = df["rsi14"]
    downtrend = c < df["sma50"]  # genuinely weak / below 50-DMA
    was_oversold = (
        rsi.rolling(5).min() < p["rsi_os"]
    )  # knife was falling (deeply oversold)
    rsi_turning = rsi > rsi.shift(1)  # momentum ticking back up
    reversal_bar = (c > c.shift(1)) & (c > o)  # a bullish reversal candle
    volp = df["vol_ratio"] > 1.0  # buyers stepping in
    bounce = downtrend & was_oversold & rsi_turning & reversal_bar & volp
    # confirmed turn: reclaiming the 50-DMA from below, with momentum + MACD flip
    reclaim = (
        (c > df["sma50"])
        & (c.shift(1) <= df["sma50"].shift(1))
        & (rsi > 50)
        & (df["macd_hist"] > 0)
    )
    R = bounce | reclaim

    # ---- COMBINED: regime switch on the 200-DMA ----
    # Above 200-DMA -> trend logic (A). Below -> reversal logic (R). Mutually exclusive.
    above_200 = df["pct_vs_sma200"] > 0
    C = (above_200 & A) | (~above_200 & R)

    # tag every bar with which regime's logic is firing (used by the combined backtest)
    ttype = pd.Series("", index=df.index)
    ttype[A.fillna(False)] = "UPTREND"
    ttype[(R.fillna(False)) & (~A.fillna(False))] = "DOWNTREND"
    df["trade_type"] = ttype

    df["branch_momentum"] = A.astype(int)
    df["branch_breakout"] = B.astype(int)
    df["branch_reversal"] = R.astype(int)
    passes = {
        "PASS_recommended": A,
        "PASS_tight": A & vol_ok,
        "PASS_balanced": A | B,
        "PASS_reversal": R,
        "PASS_combined": C,
    }
    sig = passes[strategy].fillna(False)
    if require_rs and bench_close is not None:
        sig = sig & (df["rs_roll"] > 0)  # only take longs that are beating the market
    df["signal"] = sig.fillna(False)
    return df


# ======================================================================================
#  4. BACKTEST  (triple-barrier: take-profit / stop-loss / time-stop; overlapping trades)
# ======================================================================================
SNAP_COLS = [
    "pct_vs_sma200",
    "pct_vs_sma20",
    "rsi14",
    "roc10",
    "atr_pct",
    "vol_ratio",
    "macd_hist",
    "adx14",
    "bb_pctB",
    "dist_52wH",
    "obv_slope10",
]


def run_backtest(
    df: pd.DataFrame,
    target_pct: float,
    max_hold: int,
    stop_method: str,
    stop_value: float,
    cost_pct: float = 0.20,
    apply_stcg: bool = True,
    rev_target_pct: float = None,
    rev_stop_value: float = None,
    exit_mode: str = "Trailing",
    trail_mult: float = 2.0,
    max_stop_pct: float = 5.0,
    max_atr_pct: float = None,
    entry_mode: str = "Market open",
    limit_pct: float = 0.0,
    fill_days: int = 1,
    lock_pct: float = None,
    cut_day: int = None,
    cut_threshold: float = 0.0,
    partial_frac: float = 0.0,
    partial_atr: float = 1.5,
    stop_anchor: str = "ATR",
    trail_anchor: str = "ATR",
) -> pd.DataFrame:
    o = df["Open"].values
    h = df["High"].values
    l = df["Low"].values
    c = df["Close"].values
    atr = df["atr14"].values
    atrp = df["atr_pct"].values
    sig = df["signal"].values
    ttype = (
        df["trade_type"].values
        if "trade_type" in df.columns
        else np.array([""] * len(df))
    )
    idx = df.index
    n = len(df)
    snaps = {col: df[col].values for col in SNAP_COLS}
    trades = []

    for i in range(n - 1):
        if not sig[i]:
            continue
        # VOLATILITY CEILING: skip entries when the stock is too wild to stop-loss safely
        if max_atr_pct is not None and np.isfinite(atrp[i]) and atrp[i] > max_atr_pct:
            continue
        # ---------------- ENTRY ----------------
        # Market open  : buy at next day's open, whatever the gap (old behaviour).
        # Limit        : place a resting buy at signal_close * (1 - limit_pct/100).
        #                Fill only if price trades down to it within `fill_days` sessions.
        #                A gap-DOWN opening below the limit fills at the open (better price).
        #                If it never trades there, the order expires -> NO TRADE (chase avoided).
        signal_close = c[i]
        if entry_mode == "Market open":
            entry_idx = i + 1
            if entry_idx >= n:
                break
            entry = o[entry_idx]
            limit_price = np.nan
        else:
            limit_price = signal_close * (1 - limit_pct / 100.0)
            entry_idx, entry = None, None
            for d in range(i + 1, min(i + 1 + max(int(fill_days), 1), n)):
                if o[d] <= limit_price:  # gapped below the limit -> fill at open
                    entry_idx, entry = d, o[d]
                    break
                if (
                    l[d] <= limit_price
                ):  # traded down through the limit -> fill at limit
                    entry_idx, entry = d, limit_price
                    break
            if entry_idx is None:  # never filled: skip, don't chase
                continue
        if entry is None or not np.isfinite(entry) or entry <= 0:
            continue

        # regime-aware exits: downtrend/reversal trades use tighter target & stop if provided
        is_rev = ttype[i] == "DOWNTREND"
        tp = rev_target_pct if (is_rev and rev_target_pct is not None) else target_pct
        sv = rev_stop_value if (is_rev and rev_stop_value is not None) else stop_value

        a = atr[i]
        target = entry * (1 + tp / 100)
        if stop_anchor == "Structure":
            # STRUCTURE stop: just below the lowest low of the prior 10 sessions (recent
            # support / channel floor), with a small ATR buffer so ordinary wicks don't tag it.
            if not np.isfinite(a) or a <= 0:
                continue
            swing = np.nanmin(l[max(0, i - 9) : i + 1])
            init_stop = swing - 0.25 * a
        elif stop_method == "ATR":
            if not np.isfinite(a) or a <= 0:
                continue
            init_stop = entry - sv * a
        else:  # fixed %
            init_stop = entry * (1 - sv / 100)

        # MAX-STOP CAP: never risk more than max_stop_pct from entry, whatever ATR says
        if max_stop_pct is not None:
            floor_stop = entry * (1 - max_stop_pct / 100)
            init_stop = max(init_stop, floor_stop)  # pull a too-wide stop closer
        atr_dist = entry - init_stop  # trailing distance = actual risk distance

        last = min(entry_idx + max_hold, n - 1)
        stop = init_stop
        peak = entry
        hit_target = (
            False  # did price actually reach the 10% objective during the hold?
        )
        outcome, exit_price, exit_idx = None, None, None

        # --- DYNAMIC partial-profit level: volatility-scaled, NOT a fixed % ---
        # A calm stock books its partial at a smaller move than a wild one, because for a calm
        # stock a 1.5-ATR move is already a meaningful advance.
        partial_level = (
            entry + partial_atr * a
            if (partial_frac > 0 and np.isfinite(a) and a > 0)
            else np.inf
        )
        partial_taken, partial_ret = False, 0.0

        for d in range(entry_idx, last + 1):
            day_k = d - entry_idx

            # --- STOP first, with GAP-AWARE fill ---
            if l[d] <= stop:
                fill = (
                    o[d] if o[d] < stop else stop
                )  # gapped past the stop -> fill at open
                outcome, exit_price, exit_idx = "STOP", fill, d
                break

            if exit_mode == "Fixed target":
                if h[d] >= target:  # classic barrier: caps upside
                    fill = o[d] if o[d] > target else target
                    outcome, exit_price, exit_idx = "TARGET", fill, d
                    break
            else:
                # --- TRAILING: the target is a MINIMUM objective, never a ceiling ---
                if (not partial_taken) and h[d] >= partial_level:
                    partial_taken = True
                    partial_ret = (
                        partial_level / entry - 1
                    ) * 100  # book `partial_frac` here

                if h[d] >= target and not hit_target:
                    hit_target = True
                    # PROFIT LOCK: once the 10% objective is reached, never give it all back.
                    if lock_pct is not None:
                        stop = max(stop, entry * (1 + lock_pct / 100))

                if h[d] > peak:
                    peak = h[d]
                    if trail_anchor == "Structure":
                        # trail below the rising 5-day swing low: survives ordinary pullbacks
                        # inside a trend channel, exits when support actually breaks
                        sw = np.nanmin(l[max(0, d - 4) : d + 1])
                        buf = 0.25 * atr[d] if np.isfinite(atr[d]) else 0.0
                        stop = max(stop, sw - buf)
                    else:
                        stop = max(
                            stop, peak - atr_dist
                        )  # trail up under the rising peak

            # --- CONVICTION EXIT: if it isn't working early, free the capital ---
            # Only applies before the objective is reached and before a partial is booked.
            if (
                cut_day is not None
                and day_k == cut_day
                and not hit_target
                and not partial_taken
                and (c[d] / entry - 1) * 100 < cut_threshold
            ):
                outcome, exit_price, exit_idx = "CUT", c[d], d
                break

        if outcome is None:
            outcome, exit_price, exit_idx = "TIME", c[last], last

        # Relabel so TARGET always means "reached the objective", in both modes.
        if exit_mode != "Fixed target" and outcome in ("STOP", "TIME"):
            if hit_target and exit_price >= entry:
                outcome = "TARGET"
            elif exit_price > entry:
                outcome = "TRAIL"

        # ---- blended return when a partial was booked ----
        final_ret = (exit_price / entry - 1) * 100
        if partial_taken:
            gross = partial_frac * partial_ret + (1 - partial_frac) * final_ret
        else:
            gross = final_ret
        net = gross - cost_pct
        if apply_stcg and net > 0:
            net *= 1 - 0.20  # 20% STCG on gains (simplified)

        row = {
            "signal_date": idx[i].date(),
            "signal_close": round(float(signal_close), 2),
            "limit_price": (
                round(float(limit_price), 2) if np.isfinite(limit_price) else np.nan
            ),
            "entry_date": idx[entry_idx].date(),
            "entry_price": round(entry, 2),
            "fill_edge_%": round(
                (signal_close / entry - 1) * 100, 2
            ),  # +ve = bought below signal close
            "target_price": round(target, 2),
            "stop_price": round(stop, 2),
            "exit_date": idx[exit_idx].date(),
            "exit_price": round(exit_price, 2),
            "days_held": max(exit_idx - entry_idx, 1),
            "outcome": outcome,
            "hit_target": bool(hit_target),
            "partial_taken": bool(partial_taken),
            "partial_at_%": round(partial_ret, 2) if partial_taken else np.nan,
            "peak_gain_%": round((peak / entry - 1) * 100, 2),
            "trade_type": ttype[i] if ttype[i] else "UPTREND",
            "gross_return_%": round(gross, 2),
            "net_return_%": round(net, 2),
        }
        for col in SNAP_COLS:
            row[col] = (
                round(float(snaps[col][i]), 2) if np.isfinite(snaps[col][i]) else np.nan
            )
        trades.append(row)

    return pd.DataFrame(trades)


def summarize(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {}
    n = len(trades)
    tgt = int((trades["outcome"] == "TARGET").sum())
    stp = int((trades["outcome"] == "STOP").sum())
    tim = int((trades["outcome"] == "TIME").sum())
    trl = int((trades["outcome"] == "TRAIL").sum())  # trailing profit, below 10% target
    cut = int(
        (trades["outcome"] == "CUT").sum()
    )  # conviction exit (dead trade, freed capital)
    wins = int((trades["net_return_%"] > 0).sum())
    time_df = trades[trades["outcome"] == "TIME"]
    time_win = int((time_df["net_return_%"] > 0).sum())
    time_loss = int((time_df["net_return_%"] <= 0).sum())
    win_trades = trades[trades["outcome"] == "TARGET"]
    med_days_to_target = (
        float(win_trades["days_held"].median()) if len(win_trades) else np.nan
    )
    return {
        "trades": n,
        "target_hits": tgt,
        "stop_hits": stp,
        "time_exits": tim,
        "trail_exits": trl,
        "time_win": time_win,
        "time_loss": time_loss,
        "hit_rate_%": round(100 * tgt / n, 1),
        "target_pct_of_all": round(100 * tgt / n, 1),
        "trail_pct_of_all": round(100 * trl / n, 1),
        "stop_pct_of_all": round(100 * stp / n, 1),
        "time_pct_of_all": round(100 * tim / n, 1),
        "profitable_%": round(100 * wins / n, 1),
        "avg_net_%": round(trades["net_return_%"].mean(), 2),
        "expectancy_%": round(trades["net_return_%"].mean(), 2),
        "avg_win_%": (
            round(trades.loc[trades["net_return_%"] > 0, "net_return_%"].mean(), 2)
            if wins
            else 0.0
        ),
        "avg_loss_%": (
            round(trades.loc[trades["net_return_%"] <= 0, "net_return_%"].mean(), 2)
            if wins < n
            else 0.0
        ),
        "avg_days": round(trades["days_held"].mean(), 1),
        "med_days_to_target": med_days_to_target,
        "n_winners": len(win_trades),
        "cut_exits": cut,
        "cut_pct_of_all": round(100 * cut / n, 1),
        # --- EXPECTANCY PER DAY: return earned per day of capital tied up (the metric that
        # matters when you rotate capital between stocks rather than buy-and-hold). ---
        "exp_per_day_%": round(
            trades["net_return_%"].mean() / max(trades["days_held"].mean(), 1e-9), 3
        ),
        "partials_taken": (
            int(trades.get("partial_taken", pd.Series(dtype=bool)).sum())
            if "partial_taken" in trades
            else 0
        ),
        "avg_peak_gain_%": (
            round(trades["peak_gain_%"].mean(), 2)
            if "peak_gain_%" in trades
            else np.nan
        ),
    }


# ======================================================================================
#  5. STREAMLIT UI
# ======================================================================================
STRATEGY_HELP = {
    "PASS_recommended": "Core rule: strong uptrend (price >X% above 200-DMA) AND OBV rising. "
    "Best balance of hit-rate and coverage.",
    "PASS_tight": "Strictest: uptrend AND OBV rising AND enough volatility (ATR%). "
    "Fewer, higher-conviction trades.",
    "PASS_balanced": "Widest net: momentum-continuation OR early breakout-thrust branch. "
    "Catches more winners at a slightly lower hit-rate.",
    "PASS_reversal": "COUNTER-TREND (below the 200-DMA): buys oversold bounces and 50-DMA "
    "reclaims — only after a confirmed turn. Rare, higher-risk, for downtrends.",
    "PASS_combined": "ADAPTIVE: uses the 200-DMA as a regime switch — trend logic when the stock "
    "is above it, reversal logic when below. Trades in BOTH up and down trends.",
}


def main():
    st.set_page_config(page_title="NSE Swing Screener & Backtester", layout="wide")
    st.title("📈 NSE Swing-Trade Screener & Backtester")
    st.caption(
        "Triple-barrier swing backtest with the technical filters from our research. "
        "Educational tool — not investment advice."
    )

    # ---------------- Sidebar controls ----------------
    with st.sidebar:
        st.header("1 · Instrument & data")
        ticker = st.text_input(
            "Yahoo ticker",
            value="HUDCO.NS",
            help="Use .NS for NSE, .BO for BSE (e.g. HUDCO.NS).",
        )
        today = dt.date.today()
        default_start = dt.date(2017, 6, 1)
        col1, col2 = st.columns(2)
        start = col1.date_input(
            "Start date",
            value=default_start,
            min_value=dt.date(2000, 1, 1),
            max_value=today,
        )
        end = col2.date_input(
            "End date", value=today, min_value=dt.date(2000, 1, 1), max_value=today
        )
        st.info(
            "**How much data?** Use **5+ years, ideally full history**. A range covering "
            "only a bull market (e.g. 2020–2024) flatters results — include down/choppy "
            "years (2018–19, 2022) so the edge is genuinely stress-tested."
        )

        st.header("2 · Strategy")
        strategy = st.selectbox(
            "Filter logic",
            [
                "PASS_recommended",
                "PASS_tight",
                "PASS_balanced",
                "PASS_reversal",
                "PASS_combined",
            ],
        )
        st.caption(STRATEGY_HELP[strategy])
        if strategy == "PASS_reversal":
            st.warning(
                "Counter-trend mode buys weakness. It fires rarely and carries higher risk "
                "(catching falling knives). Use small size, tighter targets, and treat it "
                "as a secondary strategy — validate across many stocks first."
            )
        if strategy == "PASS_combined":
            st.info(
                "Uptrend trades use the main target/stop below. Downtrend (reversal) trades "
                "use their own tighter target/stop, since bounces are smaller than trends."
            )

        st.header("3 · Trade rules")
        entry_choice = st.radio(
            "Entry style",
            ["Limit near signal close (recommended)", "Market at next open"],
            help="Market buys whatever the open gives you — a gap-up means a worse "
            "fill. Limit places a resting buy and simply skips the trade if "
            "price never comes back to it.",
        )
        if entry_choice.startswith("Limit"):
            entry_mode = "Limit"
            limit_pct = st.slider(
                "Limit below signal close (%)",
                0.0,
                5.0,
                0.5,
                0.1,
                help="0 = buy at the signal close price. Higher = wait for a deeper "
                "pullback (better fills, but more trades never fill).",
            )
            fill_days = st.number_input(
                "Order valid for (sessions)",
                1,
                5,
                1,
                help="How many days the limit order rests before expiring.",
            )
        else:
            entry_mode, limit_pct, fill_days = "Market open", 0.0, 1
        exit_mode = st.radio(
            "Exit style",
            ["Trailing stop (let winners run)", "Fixed target"],
            index=0,
            help="Fixed target caps gains at your target. Trailing stop removes "
            "the ceiling and exits only on a pullback — so a big move is captured.",
        )
        target_pct = st.number_input(
            "Minimum return objective (%)",
            1.0,
            100.0,
            10.0,
            0.5,
            help="In Trailing mode this is a MINIMUM, not a cap: once reached, "
            "the trade keeps running while the trend holds. In Fixed-target "
            "mode it caps the gain.",
        )
        trail_mult, lock_pct = 2.0, None
        if exit_mode.startswith("Trailing"):
            trail_mult = st.slider(
                "Trailing distance (× ATR)",
                0.5,
                5.0,
                2.0,
                0.5,
                help="Stop trails this far below the highest price reached. "
                "Wider = lets it breathe and run further.",
            )
            lock_on = st.checkbox(
                "Lock in profit once objective reached",
                value=True,
                help="Once the stock touches +10%, raise the stop so the trade can "
                "never end below the locked level. Protects the objective while "
                "still letting it run to 20-30%.",
            )
            lock_pct = (
                st.slider(
                    "Lock profit at (%)",
                    0.0,
                    30.0,
                    7.0,
                    0.5,
                    help="Floor under a winner after it hits the objective.",
                )
                if lock_on
                else None
            )
            exit_mode = "Trailing"
        else:
            exit_mode = "Fixed target"
        cA, cB = st.columns(2)
        min_hold = cA.number_input(
            "Min holding (days)",
            1,
            60,
            7,
            help="Advisory. Stop-loss is always active; "
            "the max value below is the hard time-stop.",
        )
        max_hold = cB.number_input("Max holding (days)", 1, 120, 10)

        st.header("3b · Conviction exit & partial profit")
        cut_on = st.checkbox(
            "Cut dead trades early",
            value=False,
            help="If the trade is still red after N days it rarely reaches the "
            "objective — free the capital for the next signal.",
        )
        if cut_on:
            cut_day = st.number_input("Cut if still below threshold on day", 1, 10, 2)
            cut_threshold = st.slider("…and return is below (%)", -8.0, 2.0, 0.0, 0.5)
        else:
            cut_day, cut_threshold = None, 0.0
        partial_on = st.checkbox(
            "Take partial profit (volatility-scaled)",
            value=False,
            help="Books part of the position at entry + k×ATR — so a calm stock "
            "banks at a smaller move than a wild one. Not a fixed %.",
        )
        if partial_on:
            st.caption(
                "⚠️ On HUDCO this REDUCED return per day at every setting — it caps winners. "
                "Test on your own basket before enabling."
            )
            partial_frac = st.slider("Fraction to book", 0.0, 0.9, 0.3, 0.1)
            partial_atr = st.slider("Book at entry + (× ATR)", 0.5, 4.0, 3.0, 0.25)
        else:
            partial_frac, partial_atr = 0.0, 1.5

        st.header("4 · Stop-loss")
        stop_anchor = st.radio(
            "Initial stop anchoring",
            ["ATR distance", "Structure (below 10-day swing low)"],
            help="ATR = fixed volatility distance from entry. Structure = just "
            "below recent support, so a normal pullback inside a rising "
            "channel doesn't stop you out.",
        )
        stop_anchor = "Structure" if stop_anchor.startswith("Structure") else "ATR"
        trail_anchor = st.radio(
            "Trailing anchoring",
            ["ATR distance", "Structure (below rising 5-day swing low)"],
            help="Structure trailing exits only when support actually breaks — "
            "bigger winners per trade, longer holds.",
        )
        trail_anchor = "Structure" if trail_anchor.startswith("Structure") else "ATR"
        stop_method = st.selectbox("Stop type", ["ATR (volatility-based)", "Fixed %"])
        if stop_method.startswith("ATR"):
            stop_value = st.slider(
                "ATR multiple",
                0.5,
                5.0,
                2.0,
                0.5,
                help="Stop = entry − (multiple × ATR14). 2× is a typical swing setting.",
            )
            stop_method = "ATR"
        else:
            stop_value = st.slider("Stop-loss (%)", 1.0, 20.0, 5.0, 0.5)
            stop_method = "FIXED"
        max_stop_pct = st.slider(
            "Max loss cap (%)",
            2.0,
            20.0,
            5.0,
            0.5,
            help="Hard ceiling on risk: an ATR stop wider than this is pulled "
            "in. Caps your worst-case loss per trade.",
        )
        max_atr_pct = st.slider(
            "Skip if ATR% above",
            3.0,
            15.0,
            8.0,
            0.5,
            help="Volatility ceiling: don't enter stocks so wild that a safe "
            "stop is impossible. Set high to disable.",
        )

        st.header("5 · Costs")
        cost_pct = st.number_input(
            "Round-trip cost (%)",
            0.0,
            5.0,
            0.20,
            0.05,
            help="Brokerage + STT + slippage per trade, applied to each trade.",
        )
        apply_stcg = st.checkbox(
            "Apply 20% STCG on gains (approx.)",
            value=True,
            help="ON by default: a backtest that ignores tax overstates the edge.",
        )

        rev_target_pct, rev_stop_value = None, None
        if strategy in ("PASS_combined", "PASS_reversal"):
            st.header("4b · Reversal-trade risk")
            rev_target_pct = st.number_input(
                "Reversal target (%)",
                1.0,
                100.0,
                6.0,
                0.5,
                help="Smaller target for counter-trend bounces.",
            )
            rev_stop_value = st.slider(
                "Reversal stop (× ATR)",
                0.5,
                5.0,
                1.5,
                0.5,
                help="Tighter stop for counter-trend trades.",
            )
            if stop_method == "FIXED":
                rev_stop_value = st.slider(
                    "Reversal stop (%)", 1.0, 20.0, 4.0, 0.5, key="rev_fixed"
                )

        st.header("6 · Filter thresholds")
        with st.expander("Advanced (defaults are HUDCO-derived)"):
            p = {
                "regime": st.slider("Uptrend: % above 200-DMA", 0.0, 50.0, 15.0, 1.0),
                "atr": st.slider("Volatility floor: ATR%", 0.0, 10.0, 3.5, 0.5),
                "roc": st.slider("Breakout branch: ROC(10) >", 0.0, 15.0, 3.0, 0.5),
                "volr": st.slider(
                    "Breakout branch: volume ratio >", 0.5, 4.0, 1.2, 0.1
                ),
                "rsi_os": st.slider(
                    "Reversal branch: oversold RSI <", 10.0, 45.0, 30.0, 1.0
                ),
            }
        run = st.button("🚀 Run backtest", type="primary", use_container_width=True)

    if not run:
        st.write("Set your parameters in the sidebar and click **Run backtest**.")
        st.stop()

    # ---------------- Pipeline ----------------
    with st.spinner(f"Fetching {ticker} …"):
        try:
            raw = fetch_data(ticker, start, end)
        except Exception as e:
            st.error(f"Data fetch failed: {e}")
            st.stop()
    if raw.empty:
        st.error(
            "No data returned. Check the ticker (NSE needs the .NS suffix) and date range."
        )
        st.stop()

    df = compute_indicators(raw)
    df = generate_signals(df, strategy, p)
    trades = run_backtest(
        df,
        target_pct,
        int(max_hold),
        stop_method,
        stop_value,
        cost_pct,
        apply_stcg,
        rev_target_pct=rev_target_pct,
        rev_stop_value=rev_stop_value,
        exit_mode=exit_mode,
        trail_mult=trail_mult,
        max_stop_pct=max_stop_pct,
        max_atr_pct=max_atr_pct,
        entry_mode=entry_mode,
        limit_pct=limit_pct,
        fill_days=int(fill_days),
        lock_pct=lock_pct,
        cut_day=(int(cut_day) if cut_day else None),
        cut_threshold=cut_threshold,
        partial_frac=partial_frac,
        partial_atr=partial_atr,
        stop_anchor=stop_anchor,
        trail_anchor=trail_anchor,
    )
    n_signals = int(df["signal"].fillna(False).sum())
    if entry_mode == "Limit" and n_signals:
        fill_rate = 100.0 * len(trades) / n_signals
        st.info(
            f"📥 **Limit entry:** {len(trades)} of {n_signals} signals filled "
            f"({fill_rate:.0f}%). The unfilled ones ran away without you — that is the cost of "
            f"not chasing. Average fill edge: "
            f"{trades['fill_edge_%'].mean():+.2f}% vs the signal close."
            if len(trades)
            else f"📥 **Limit entry:** 0 of {n_signals} signals filled — try a smaller limit % "
            f"or more valid sessions."
        )
    stats = summarize(trades)

    st.success(
        f"Loaded {len(df)} trading days for {ticker} "
        f"({df.index[0].date()} → {df.index[-1].date()})."
    )

    if trades.empty:
        st.warning(
            "No signals fired for this strategy over this window. "
            "Try PASS_balanced or a longer date range."
        )
        st.stop()

    # ---------------- Headline metrics ----------------
    st.subheader("Results")
    m = st.columns(4)
    m[0].metric("Total trades", stats["trades"])
    m[1].metric("Target hits", stats["target_hits"], f"{stats['hit_rate_%']}% hit-rate")
    m[2].metric("Stop-loss hits", stats["stop_hits"])
    m[3].metric("Time exits", stats["time_exits"])
    m2 = st.columns(4)
    m2[0].metric("Profitable trades", f"{stats['profitable_%']}%")
    m2[1].metric(
        "Expectancy / trade",
        f"{stats['expectancy_%']}%",
        f"{stats.get('exp_per_day_%', 0)}% per day",
    )
    m2[2].metric(
        "Avg win / avg loss", f"{stats['avg_win_%']}% / {stats['avg_loss_%']}%"
    )
    m2[3].metric("Avg holding", f"{stats['avg_days']} days")

    st.caption(
        "**Hit-rate** = share of trades that reached your target. **Profitable %** also "
        "counts time-exits that closed green. **Expectancy** is the average net return per "
        "trade — the number that decides if the system makes money."
    )

    # ---- regime split (only meaningful for combined / mixed strategies) ----
    if trades["trade_type"].nunique() > 1:
        st.markdown(
            "**Performance by regime** — how the uptrend and downtrend legs each contribute:"
        )
        rows = []
        for rt, sub in trades.groupby("trade_type"):
            wins = (sub["net_return_%"] > 0).mean() * 100
            rows.append(
                {
                    "regime": rt,
                    "trades": len(sub),
                    "target hits": int((sub["outcome"] == "TARGET").sum()),
                    "stop hits": int((sub["outcome"] == "STOP").sum()),
                    "profitable %": round(wins, 1),
                    "expectancy %": round(sub["net_return_%"].mean(), 2),
                    "avg days": round(sub["days_held"].mean(), 1),
                }
            )
        st.dataframe(pd.DataFrame(rows).set_index("regime"), use_container_width=True)
        st.caption(
            "If the DOWNTREND row's expectancy is negative for a given stock, the reversal "
            "leg is hurting you on that name — favour the trend leg there."
        )

    # ---------------- Price chart with trade outcomes ----------------
    st.subheader("Price & trade outcomes")
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.04,
        subplot_titles=(
            "Close price with entries",
            "Cumulative net return (overlapping proxy)",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["Close"], name="Close", line=dict(color="#334155", width=1)
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["sma200"],
            name="200-DMA",
            line=dict(color="#f59e0b", width=1, dash="dot"),
        ),
        row=1,
        col=1,
    )
    colors = {
        "TARGET": "#16a34a",
        "TRAIL": "#86efac",
        "STOP": "#dc2626",
        "TIME": "#94a3b8",
    }
    for oc, cl in colors.items():
        sub = trades[trades["outcome"] == oc]
        if not sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=pd.to_datetime(sub["entry_date"]),
                    y=sub["entry_price"],
                    mode="markers",
                    name=oc,
                    marker=dict(color=cl, size=7, line=dict(width=0.5, color="white")),
                ),
                row=1,
                col=1,
            )
    eq = trades.sort_values("entry_date").copy()
    eq["cum"] = eq["net_return_%"].cumsum()
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(eq["entry_date"]),
            y=eq["cum"],
            name="Cumulative net %",
            line=dict(color="#2563eb", width=1.5),
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        height=650,
        hovermode="x unified",
        legend_orientation="h",
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Green = target hit, red = stop hit, grey = time exit. The lower panel sums "
        "individual trade returns in entry order — a rough performance proxy, not a "
        "compounded single-capital equity curve (signals overlap)."
    )

    # ---------------- Which indicators separated winners from losers ----------------
    st.subheader("Technical parameters used & their discriminating power")
    st.markdown(
        "**Indicator suite computed each day (no look-ahead):** moving averages 5/20/50/200, "
        "RSI(14), MACD(12,26,9), ATR% , Bollinger %B & bandwidth, Stochastics, OBV & OBV-slope, "
        "ADX/+DI/−DI, volume ratio & surge, 20-day breakout, 52-week distance, candle body/gap.\n\n"
        f"**Active filter — `{strategy}`:** {STRATEGY_HELP[strategy]}"
    )
    wins = trades[trades["outcome"] == "TARGET"]
    losses = trades[trades["outcome"] == "STOP"]
    if not wins.empty and not losses.empty:
        comp = pd.DataFrame(
            {
                "target-hit avg": wins[SNAP_COLS].mean().round(2),
                "stop-hit avg": losses[SNAP_COLS].mean().round(2),
            }
        )
        comp["separation"] = (
            (comp["target-hit avg"] - comp["stop-hit avg"])
            / trades[SNAP_COLS].std().replace(0, np.nan)
        ).round(2)
        comp = comp.reindex(comp["separation"].abs().sort_values(ascending=False).index)
        st.dataframe(comp, use_container_width=True)
        st.caption(
            "Entry-day indicator averages for winning vs stopped-out trades. "
            "|separation| above ~0.5 means the indicator meaningfully tilts the odds."
        )

    # ---------------- Trade log ----------------
    st.subheader("Trade log")
    st.dataframe(trades, use_container_width=True, height=350)
    st.download_button(
        "⬇️ Download trades CSV",
        trades.to_csv(index=False).encode(),
        file_name=f"{ticker}_backtest_trades.csv",
        mime="text/csv",
    )

    st.divider()
    st.caption(
        "⚠️ Single-stock, in-sample results flatter reality. Validate across many stocks "
        "and out-of-sample before trusting any threshold. This is an educational backtest, "
        "not investment advice."
    )


if __name__ == "__main__":
    main()
