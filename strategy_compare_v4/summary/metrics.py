"""
==============================================================
Institutional Strategy Comparison Platform V4
Summary Metrics Engine
==============================================================

Computes institutional performance metrics from a
single trade log.

One CSV
↓

One metrics dictionary

==============================================================
"""

from __future__ import annotations

import pandas as pd


def safe_divide(
    numerator: float,
    denominator: float,
) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


# ==========================================================
# Helpers
# ==========================================================


def compute_trade_metrics(
    stock: str,
    df: pd.DataFrame,
) -> dict:
    trades = len(df)

    if trades == 0:
        return {
            "Stock": stock,
            "Trades": 0,
        }

    returns = pd.to_numeric(
        df["net_return_%"],
        errors="coerce",
    ).fillna(0)

    holding = pd.to_numeric(
        df["days_held"],
        errors="coerce",
    ).fillna(0)

    wins = returns > 0
    losses = returns < 0

    win_count = int(wins.sum())
    loss_count = int(losses.sum())

    win_pct = safe_divide(
        win_count * 100,
        trades,
    )

    avg_win = returns[wins].mean() if win_count else 0.0

    avg_loss = abs(returns[losses].mean()) if loss_count else 0.0

    gross_profit = returns[wins].sum()
    gross_loss = abs(returns[losses].sum())

    profit_factor = safe_divide(
        gross_profit,
        gross_loss,
    )

    reward_risk = safe_divide(
        avg_win,
        avg_loss,
    )

    expectancy = (win_pct / 100) * avg_win - ((100 - win_pct) / 100) * avg_loss

    avg_days = holding.mean()

    total_return = returns.sum()

    years = max(
        safe_divide(
            holding.sum(),
            365.25,
        ),
        1 / 365,
    )

    annual_return = safe_divide(
        total_return,
        years,
    )

    cumulative = (1 + returns / 100).cumprod()

    running_max = cumulative.cummax()

    drawdown = (cumulative / running_max - 1) * 100

    max_drawdown = abs(drawdown.min())

    volatility = returns.std()

    sharpe = safe_divide(
        returns.mean(),
        volatility,
    )

    downside = returns[returns < 0].std()

    sortino = safe_divide(
        returns.mean(),
        downside,
    )

    recovery = safe_divide(
        total_return,
        max_drawdown,
    )

    cagr = (cumulative.iloc[-1] ** (1 / years) - 1) * 100

    # --------------------------------------------------
    # Exit Statistics
    # --------------------------------------------------

    target_count = 0
    trail_count = 0
    stop_count = 0
    time_count = 0

    exit_column = None

    possible_exit_columns = [
        "exit_reason",
        "Exit Reason",
        "ExitReason",
        "exit_type",
        "Exit Type",
        "Exit",
        "Reason",
    ]

    for col in possible_exit_columns:
        if col in df.columns:
            exit_column = col
            break

    if exit_column is not None:
        exit_series = df[exit_column].astype(str).str.upper()

        target_count = int(exit_series.str.contains("TARGET").sum())

        trail_count = int(exit_series.str.contains("TRAIL").sum())

        stop_count = int(exit_series.str.contains("STOP").sum())

        time_count = int(
            (exit_series.str.contains("TIME") | exit_series.str.contains("EXPIR")).sum()
        )

    target_pct = safe_divide(
        target_count * 100,
        trades,
    )

    trail_pct = safe_divide(
        trail_count * 100,
        trades,
    )

    stop_pct = safe_divide(
        stop_count * 100,
        trades,
    )

    time_pct = safe_divide(
        time_count * 100,
        trades,
    )

    return {
        "Stock": stock,
        "Trades": trades,
        "Wins": win_count,
        "Losses": loss_count,
        "Win%": round(win_pct, 2),
        "Avg Win %": round(avg_win, 2),
        "Avg Loss %": round(avg_loss, 2),
        "Profit Factor": round(profit_factor, 3),
        "Reward Risk": round(reward_risk, 3),
        "Expectancy": round(expectancy, 3),
        "Avg days": round(avg_days, 2),
        "Years": round(years, 2),
        "Annual Return %": round(annual_return, 2),
        "CAGR": round(cagr, 2),
        "Max Drawdown %": round(max_drawdown, 2),
        "Sharpe": round(sharpe, 3),
        "Sortino": round(sortino, 3),
        "Recovery Factor": round(recovery, 3),
        "Target #": target_count,
        "Trail #": trail_count,
        "Stop #": stop_count,
        "Time #": time_count,
        "Target %": round(target_pct, 2),
        "Trail %": round(trail_pct, 2),
        "Stop %": round(stop_pct, 2),
        "Time %": round(time_pct, 2),
    }


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "compute_trade_metrics",
]
