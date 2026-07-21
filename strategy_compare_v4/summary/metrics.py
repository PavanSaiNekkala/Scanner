"""
==============================================================
Institutional Strategy Comparison Platform V5
Summary Metrics Engine

Part 1
-------
Foundation & Helper Utilities

Responsible for

• Data validation
• Safe mathematical operations
• Column normalization
• Date parsing
• Statistical helpers
• Equity curve utilities
• Drawdown utilities

==============================================================
"""

from __future__ import annotations

import logging
from typing import Any, cast

import numpy as np
import pandas as pd

MetricsDict = dict[str, Any]

logger = logging.getLogger(__name__)

# ==========================================================
# Configuration
# ==========================================================

INITIAL_CAPITAL = 100.0

EPSILON = 1e-12


# ==========================================================
# Required Columns
# ==========================================================

REQUIRED_COLUMNS = {
    "net_return_%",
    "days_held",
}


# ==========================================================
# Exit Column Candidates
# ==========================================================

EXIT_COLUMNS = (
    "outcome",
    "Outcome",
    "exit_reason",
    "Exit Reason",
    "ExitReason",
    "exit_type",
    "Exit Type",
    "Exit",
    "Reason",
)


# ==========================================================
# Date Column Candidates
# ==========================================================

ENTRY_DATE_COLUMNS = (
    "entry_date",
    "Entry Date",
    "EntryDate",
    "buy_date",
    "signal_date",
)

EXIT_DATE_COLUMNS = (
    "exit_date",
    "Exit Date",
    "ExitDate",
    "sell_date",
)


# ==========================================================
# Safe Helpers
# ==========================================================


def safe_divide(numerator, denominator):

    if abs(denominator) < EPSILON:
        if numerator > 0:
            return float("inf")

        return 0.0

    """
    Safe division.

    Returns zero when denominator is zero.
    """

    if abs(denominator) < EPSILON:
        return 0.0

    return float(numerator) / float(denominator)


def safe_mean(
    values: pd.Series[Any],
) -> float:
    """
    Mean ignoring NaNs.
    """

    if values.empty:
        return 0.0

    return float(values.mean())


def safe_median(
    values: pd.Series[Any],
) -> float:
    """
    Median ignoring NaNs.
    """

    if values.empty:
        return 0.0

    return float(values.median())


def safe_std(
    values: pd.Series[Any],
) -> float:
    """
    Standard deviation.
    """

    if len(values) < 2:
        return 0.0

    return float(values.std())


def safe_min(
    values: pd.Series[Any],
) -> float:
    if values.empty:
        return 0.0

    return float(values.min())


def safe_max(
    values: pd.Series[Any],
) -> float:
    if values.empty:
        return 0.0

    return float(values.max())


# ==========================================================
# Validation
# ==========================================================


def validate_trade_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Validate required columns.
    """

    missing = REQUIRED_COLUMNS.difference(df.columns)

    if missing:
        logger.error(
            "Missing required columns: %s",
            sorted(missing),
        )

        raise KeyError(f"Missing required columns: {sorted(missing)}")


# ==========================================================
# Numeric Conversion
# ==========================================================


def numeric(
    series: pd.Series[Any],
) -> pd.Series[float]:
    """
    Convert Series to numeric.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    ).astype(float)


# ==========================================================
# Date Conversion
# ==========================================================


def datetime_series(
    series: pd.Series,
) -> pd.Series:
    """
    Convert Series to datetime.
    """

    return pd.to_datetime(
        series,
        errors="coerce",
    )


# ==========================================================
# Column Detection
# ==========================================================


def find_column(
    df: pd.DataFrame,
    candidates: tuple[str, ...],
) -> str | None:
    """
    Find first matching column.
    """

    normalized = {c.strip().lower(): c for c in df.columns}

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


# ==========================================================
# Exit Column
# ==========================================================


def detect_exit_column(
    df: pd.DataFrame,
) -> str | None:
    """
    Detect exit reason column.
    """

    return find_column(
        df,
        EXIT_COLUMNS,
    )


# ==========================================================
# Entry / Exit Dates
# ==========================================================


def detect_entry_column(
    df: pd.DataFrame,
) -> str | None:
    return find_column(
        df,
        ENTRY_DATE_COLUMNS,
    )


def detect_exit_date_column(
    df: pd.DataFrame,
) -> str | None:
    return find_column(
        df,
        EXIT_DATE_COLUMNS,
    )


# ==========================================================
# Calendar Years
# ==========================================================


def calculate_calendar_years(
    df: pd.DataFrame,
) -> float:
    """
    Calculate elapsed calendar years.

    Uses first entry date and last exit date.

    Falls back to holding period if
    dates are unavailable.
    """

    entry_col = detect_entry_column(df)

    exit_col = detect_exit_date_column(df)

    if entry_col is not None and exit_col is not None:
        start = datetime_series(df[entry_col]).min()

        end = datetime_series(df[exit_col]).max()

        if pd.notna(start) and pd.notna(end) and end > start:
            days = (end - start).days

            return max(
                days / 365.25,
                1 / 365,
            )

    holding = numeric(df["days_held"])

    return max(
        holding.sum() / 365.25,
        1 / 365,
    )


# ==========================================================
# Equity Curve
# ==========================================================


def build_equity_curve(
    returns: pd.Series,
    initial_capital: float = INITIAL_CAPITAL,
) -> pd.Series:
    """
    Build cumulative equity curve.

    Trade-by-trade.
    """

    cumulative = (1.0 + returns / 100.0).cumprod()

    return cumulative * initial_capital


# ==========================================================
# Running Peak
# ==========================================================


def running_peak(
    equity: pd.Series,
) -> pd.Series:
    """
    Running equity high.
    """

    return equity.cummax()


# ==========================================================
# Drawdown
# ==========================================================


def drawdown_series(
    equity: pd.Series,
) -> pd.Series:
    """
    Drawdown percentage.
    """

    peak = running_peak(equity)

    return (equity / peak - 1.0) * 100.0


# ==========================================================
# Maximum Drawdown
# ==========================================================


def maximum_drawdown(
    equity: pd.Series,
) -> float:
    """
    Maximum drawdown.
    """

    dd = drawdown_series(equity)

    return abs(float(dd.min()))


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "INITIAL_CAPITAL",
    "EPSILON",
    "numeric",
    "safe_divide",
    "safe_mean",
    "safe_median",
    "safe_std",
    "safe_min",
    "safe_max",
    "validate_trade_dataframe",
    "detect_exit_column",
    "detect_entry_column",
    "detect_exit_date_column",
    "calculate_calendar_years",
    "build_equity_curve",
    "drawdown_series",
    "maximum_drawdown",
]

# ==========================================================
# Trade Statistics
# ==========================================================


def trade_statistics(
    returns: pd.Series,
) -> MetricsDict:
    """
    Compute basic trade statistics.

    Parameters
    ----------
    returns
        Net trade returns (%)

    Returns
    -------
    Dictionary of trade metrics.
    """

    trades = len(returns)

    wins = returns > 0

    losses = returns < 0

    breakeven = returns == 0

    win_count = int(wins.sum())

    loss_count = int(losses.sum())

    breakeven_count = int(breakeven.sum())

    win_pct = safe_divide(
        win_count * 100,
        trades,
    )

    loss_pct = safe_divide(
        loss_count * 100,
        trades,
    )

    breakeven_pct = safe_divide(
        breakeven_count * 100,
        trades,
    )

    return {
        "Trades": trades,
        "Wins": win_count,
        "Losses": loss_count,
        "Breakeven": breakeven_count,
        "Win%": round(win_pct, 2),
        "Loss%": round(loss_pct, 2),
        "Breakeven%": round(
            breakeven_pct,
            2,
        ),
    }


# ==========================================================
# Holding Statistics
# ==========================================================


def holding_statistics(
    holding: pd.Series,
) -> MetricsDict:
    """
    Holding period statistics.
    """

    return {
        "Avg days": round(
            safe_mean(
                holding,
            ),
            2,
        ),
        "Median days": round(
            safe_median(
                holding,
            ),
            2,
        ),
        "Minimum days": round(
            safe_min(
                holding,
            ),
            2,
        ),
        "Maximum days": round(
            safe_max(
                holding,
            ),
            2,
        ),
        "Holding Std": round(
            safe_std(
                holding,
            ),
            2,
        ),
    }


# ==========================================================
# Return Statistics
# ==========================================================


def return_statistics(
    returns: pd.Series,
) -> MetricsDict:
    """
    Compute institutional return statistics.
    """
    if returns.empty:
        return {
            "Average Return %": 0.0,
            "Median Return %": 0.0,
            "Average Win %": 0.0,
            "Average Loss %": 0.0,
            "Largest Win %": 0.0,
            "Largest Loss %": 0.0,
            "Profit Factor": 0.0,
            "Reward Risk": 0.0,
            "Expectancy": 0.0,
            "Expectancy %": 0.0,
            "Payoff Ratio": 0.0,
        }

    wins = returns[returns > 0]

    losses = returns[returns < 0]

    gross_profit = wins.sum()

    gross_loss = abs(losses.sum())

    avg_win = safe_mean(
        wins,
    )

    avg_loss = abs(
        safe_mean(
            losses,
        )
    )

    median_return = safe_median(
        returns,
    )

    avg_return = safe_mean(
        returns,
    )

    largest_win = safe_max(
        returns,
    )

    largest_loss = safe_min(
        returns,
    )

    profit_factor = safe_divide(
        gross_profit,
        gross_loss,
    )

    reward_risk = safe_divide(
        avg_win,
        avg_loss,
    )

    win_rate = safe_divide(
        len(wins),
        len(returns),
    )

    loss_rate = 1 - win_rate

    expectancy = win_rate * avg_win - loss_rate * avg_loss

    expectancy_pct = (
        safe_divide(
            expectancy,
            avg_loss,
        )
        * 100
    )

    payoff_ratio = reward_risk

    return {
        "Average Return %": round(
            avg_return,
            2,
        ),
        "Median Return %": round(
            median_return,
            2,
        ),
        "Average Win %": round(
            avg_win,
            2,
        ),
        "Average Loss %": round(
            avg_loss,
            2,
        ),
        "Largest Win %": round(
            largest_win,
            2,
        ),
        "Largest Loss %": round(
            largest_loss,
            2,
        ),
        "Profit Factor": round(
            profit_factor,
            3,
        ),
        "Reward Risk": round(
            reward_risk,
            3,
        ),
        "Expectancy": round(
            expectancy,
            3,
        ),
        "Expectancy %": round(
            expectancy_pct,
            2,
        ),
        "Payoff Ratio": round(
            payoff_ratio,
            3,
        ),
    }


# ==========================================================
# Consecutive Wins / Losses
# ==========================================================


def streak_statistics(
    returns: pd.Series,
) -> dict[str, int]:
    """
    Compute longest winning
    and losing streaks.
    """

    longest_win = 0
    longest_loss = 0

    current_win = 0
    current_loss = 0

    for value in returns:
        if value > 0:
            current_win += 1
            current_loss = 0

        elif value < 0:
            current_loss += 1
            current_win = 0

        else:
            current_win = 0
            current_loss = 0

        longest_win = max(
            longest_win,
            current_win,
        )

        longest_loss = max(
            longest_loss,
            current_loss,
        )

    return {
        "Longest Winning Streak": longest_win,
        "Longest Losing Streak": longest_loss,
    }


# ==========================================================
# Risk & Performance Statistics (Trade-Based)
# ==========================================================


def volatility(
    returns: pd.Series,
) -> float:
    """
    Trade return volatility (%).
    """

    return safe_std(returns)


# ==========================================================


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    """
    Trade-based Sharpe Ratio.
    """

    if len(returns) < 2:
        return 0.0

    excess = returns - risk_free_rate

    std = excess.std()

    if abs(std) < EPSILON:
        return 0.0

    return float(excess.mean() / std)


# ==========================================================


def sortino_ratio(
    returns: pd.Series,
    target_return: float = 0.0,
) -> float:
    """
    Trade-based Sortino Ratio.
    """

    downside = returns[returns < target_return]

    if len(downside) == 0:
        return 0.0

    downside_std = downside.std()

    if abs(downside_std) < EPSILON:
        return 0.0

    return float((returns.mean() - target_return) / downside_std)


# ==========================================================


def recovery_factor(
    equity: pd.Series,
) -> float:
    """
    Recovery Factor.

    Net Profit / Max Drawdown
    """

    if equity.empty:
        return 0.0

    net_profit = (equity.iloc[-1] / equity.iloc[0] - 1) * 100

    mdd = maximum_drawdown(equity)

    return safe_divide(
        net_profit,
        mdd,
    )


# ==========================================================


def calmar_ratio(
    annual_return: float,
    max_dd: float,
) -> float:
    """
    Trade-based Calmar.
    """

    return safe_divide(
        annual_return,
        max_dd,
    )


# ==========================================================


def mar_ratio(
    cagr: float,
    max_dd: float,
) -> float:
    """
    MAR Ratio.
    """

    return safe_divide(
        cagr,
        max_dd,
    )


# ==========================================================


def ulcer_index(
    equity: pd.Series,
) -> float:
    """
    Ulcer Index.
    """

    dd = drawdown_series(equity)

    if dd.empty:
        return 0.0

    return float(np.sqrt(np.mean(np.square(dd))))


# ==========================================================


def omega_ratio(
    returns: pd.Series,
    threshold: float = 0.0,
) -> float:
    """
    Omega Ratio.
    """

    gains = returns[returns > threshold] - threshold

    losses = threshold - returns[returns < threshold]

    return safe_divide(
        gains.sum(),
        losses.sum(),
    )


# ==========================================================


def skewness(
    returns: pd.Series,
) -> float:
    """
    Return skewness.
    """

    if len(returns) < 3:
        return 0.0

    numeric_returns = cast(
        pd.Series[float],
        pd.to_numeric(
            returns,
            errors="coerce",
        ),
    )

    result = numeric_returns.skew()

    return float(
        cast(
            float,
            result,
        )
    )


# ==========================================================


def kurtosis(
    returns: pd.Series,
) -> float:
    """
    Return kurtosis.
    """

    if len(returns) < 4:
        return 0.0

    numeric_returns = cast(
        pd.Series[float],
        pd.to_numeric(
            returns,
            errors="coerce",
        ),
    )

    result = numeric_returns.kurt()

    return float(
        cast(
            float,
            result,
        )
    )


# ==========================================================


def annual_statistics(
    returns: pd.Series[Any],
    years: float,
) -> MetricsDict:
    """
    Trade-based annual metrics.
    CAGR = ((1 + Total Return)^(1/Years)-1)*100
    """

    returns = cast(
        pd.Series[float],
        pd.to_numeric(
            returns,
            errors="coerce",
        ),
    )

    growth_series = returns.astype(float).div(100.0).add(1.0)

    growth_factor = cast(
        float,
        growth_series.prod(),
    )

    total_return: float = (growth_factor - 1.0) * 100.0

    annual_return: float = total_return / years if years > 0 else 0.0

    growth: float = 1.0 + total_return / 100

    cagr: float = (
        0.0 if years <= 0 or growth <= 0 else (growth ** (1 / years) - 1) * 100
    )

    return {
        "Total Return %": round(
            total_return,
            2,
        ),
        "Annual Return %": round(
            annual_return,
            2,
        ),
        "CAGR %": round(
            cagr,
            2,
        ),
    }


# ==========================================================


def risk_statistics(
    returns: pd.Series,
    years: float,
) -> MetricsDict:
    """
    Complete trade-based
    risk statistics.
    """

    equity = build_equity_curve(returns)

    mdd = maximum_drawdown(equity)

    annual = annual_statistics(
        returns,
        years,
    )

    annual_return = annual["Annual Return %"]

    cagr = annual["CAGR %"]

    return {
        **annual,
        "Volatility": round(
            volatility(returns),
            3,
        ),
        "Sharpe": round(
            sharpe_ratio(returns),
            3,
        ),
        "Sortino": round(
            sortino_ratio(returns),
            3,
        ),
        "Omega": round(
            omega_ratio(returns),
            3,
        ),
        "Maximum Drawdown %": round(
            mdd,
            2,
        ),
        "Recovery Factor": round(
            recovery_factor(equity),
            3,
        ),
        "Calmar Ratio": round(
            calmar_ratio(
                annual_return,
                mdd,
            ),
            3,
        ),
        "MAR Ratio": round(
            mar_ratio(
                cagr,
                mdd,
            ),
            3,
        ),
        "Ulcer Index": round(
            ulcer_index(equity),
            3,
        ),
        "Skewness": round(
            skewness(returns),
            3,
        ),
        "Kurtosis": round(
            kurtosis(returns),
            3,
        ),
    }


# ==========================================================
# Exit Analytics
# ==========================================================


def normalize_exit_reason(
    value: object,
) -> str:
    """
    Normalize exit reason.

    Examples
    --------
    Target
    TARGET
    target

    -> TARGET
    """

    if value is None:
        return "UNKNOWN"

    if isinstance(value, float) and np.isnan(value):
        return "UNKNOWN"

    value = str(value).strip().upper()

    mapping = {
        "TARGET": "TARGET",
        "TARGET HIT": "TARGET",
        "TP": "TARGET",
        "STOP": "STOP",
        "STOPLOSS": "STOP",
        "STOP LOSS": "STOP",
        "SL": "STOP",
        "TRAIL": "TRAIL",
        "TRAIL STOP": "TRAIL",
        "TRAILING STOP": "TRAIL",
        "TIME": "TIME",
        "TIME EXIT": "TIME",
        "TIMEOUT": "TIME",
    }

    return mapping.get(value, value)


# ==========================================================


def exit_statistics(
    df: pd.DataFrame,
    returns: pd.Series,
) -> MetricsDict:
    """
    Institutional exit analytics.
    """

    exit_column = detect_exit_column(df)

    if exit_column is None:
        return {
            "Target #": 0,
            "Target %": 0.0,
            "Trail #": 0,
            "Trail %": 0.0,
            "Stop #": 0,
            "Stop %": 0.0,
            "Time #": 0,
            "Time %": 0.0,
            "Average Target %": 0.0,
            "Average Trail %": 0.0,
            "Average Stop %": 0.0,
            "Average Time %": 0.0,
        }

    exits = df[exit_column].apply(normalize_exit_reason)

    total = len(exits)

    target_mask = exits == "TARGET"
    stop_mask = exits == "STOP"
    trail_mask = exits == "TRAIL"
    time_mask = exits == "TIME"

    target_count = int(target_mask.sum())
    stop_count = int(stop_mask.sum())
    trail_count = int(trail_mask.sum())
    time_count = int(time_mask.sum())

    return {
        "Target #": target_count,
        "Target %": round(
            safe_divide(
                target_count * 100,
                total,
            ),
            2,
        ),
        "Trail #": trail_count,
        "Trail %": round(
            safe_divide(
                trail_count * 100,
                total,
            ),
            2,
        ),
        "Stop #": stop_count,
        "Stop %": round(
            safe_divide(
                stop_count * 100,
                total,
            ),
            2,
        ),
        "Time #": time_count,
        "Time %": round(
            safe_divide(
                time_count * 100,
                total,
            ),
            2,
        ),
        "Average Target %": round(
            safe_mean(returns[target_mask]),
            2,
        ),
        "Average Trail %": round(
            safe_mean(returns[trail_mask]),
            2,
        ),
        "Average Stop %": round(
            safe_mean(returns[stop_mask]),
            2,
        ),
        "Average Time %": round(
            safe_mean(returns[time_mask]),
            2,
        ),
    }


# ==========================================================
# Exit Quality
# ==========================================================


def exit_quality(
    exit_metrics: MetricsDict,
) -> MetricsDict:
    """
    Exit efficiency metrics.
    """

    target_pct = exit_metrics["Target %"]
    trail_pct = exit_metrics["Trail %"]
    stop_pct = exit_metrics["Stop %"]
    time_pct = exit_metrics["Time %"]

    winning_exit = target_pct + trail_pct

    losing_exit = stop_pct + time_pct

    exit_score = winning_exit - losing_exit

    return {
        "Winning Exit %": round(
            winning_exit,
            2,
        ),
        "Losing Exit %": round(
            losing_exit,
            2,
        ),
        "Exit Score": round(
            exit_score,
            2,
        ),
    }


# ==========================================================
# Trade Frequency
# ==========================================================


def frequency_statistics(
    trades: int,
    years: float,
) -> MetricsDict:
    """
    Trading frequency.
    """

    trades_per_year = safe_divide(
        trades,
        years,
    )

    trades_per_month = safe_divide(
        trades_per_year,
        12,
    )

    return {
        "Trades / Year": round(
            trades_per_year,
            2,
        ),
        "Trades / Month": round(
            trades_per_month,
            2,
        ),
    }


# ==========================================================
# Capital Efficiency
# ==========================================================


def capital_efficiency(
    returns: pd.Series,
    holding: pd.Series,
) -> MetricsDict:
    """
    Capital utilisation statistics.
    """

    avg_return = safe_mean(
        returns,
    )

    avg_days = safe_mean(
        holding,
    )

    return {
        "Return / Holding Day": round(
            safe_divide(
                avg_return,
                avg_days,
            ),
            4,
        ),
        "Holding Efficiency": round(
            safe_divide(
                365,
                avg_days,
            ),
            2,
        ),
    }


# ==========================================================
# Main Public API
# ==========================================================


def compute_trade_metrics(
    stock: str,
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Compute complete trade metrics for a strategy.

    Parameters
    ----------
    stock : str
        Stock name.

    df : DataFrame
        Trade log.

    Returns
    -------
    Dictionary containing all summary metrics.
    """

    validate_trade_dataframe(df)

    entry_column = detect_entry_column(df)

    if entry_column is not None:
        df = df.sort_values(entry_column).reset_index(drop=True)

    if df.empty:
        logger.warning(
            "Empty trade dataframe for %s",
            stock,
        )

        return {
            "Stock": stock,
            "Years": 0,
            "Trades": 0,
        }

    logger.info(
        "Computing summary metrics for %s",
        stock,
    )

    returns = numeric(df["net_return_%"])

    holding = numeric(df["days_held"])

    years = calculate_calendar_years(df)

    metrics: dict[str, Any] = {}

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    metrics["Stock"] = stock

    metrics["Years"] = round(
        years,
        2,
    )

    # ------------------------------------------------------
    # Trade Statistics
    # ------------------------------------------------------

    metrics.update(
        trade_statistics(
            returns,
        )
    )

    # ------------------------------------------------------
    # Holding Statistics
    # ------------------------------------------------------

    metrics.update(
        holding_statistics(
            holding,
        )
    )

    # ------------------------------------------------------
    # Return Statistics
    # ------------------------------------------------------

    metrics.update(
        return_statistics(
            returns,
        )
    )

    # ------------------------------------------------------
    # Streak Statistics
    # ------------------------------------------------------

    metrics.update(
        streak_statistics(
            returns,
        )
    )

    # ------------------------------------------------------
    # Risk Statistics
    # ------------------------------------------------------

    metrics.update(
        risk_statistics(
            returns,
            years,
        )
    )

    # ------------------------------------------------------
    # Exit Statistics
    # ------------------------------------------------------

    exit_metrics = exit_statistics(
        df,
        returns,
    )

    metrics.update(exit_metrics)

    metrics.update(exit_quality(exit_metrics))

    # ------------------------------------------------------
    # Frequency
    # ------------------------------------------------------

    metrics.update(
        frequency_statistics(
            metrics["Trades"],
            years,
        )
    )

    # ------------------------------------------------------
    # Capital Efficiency
    # ------------------------------------------------------

    metrics.update(
        capital_efficiency(
            returns,
            holding,
        )
    )

    # ------------------------------------------------------
    # Convenience Metrics
    # ------------------------------------------------------

    metrics["Net Profit %"] = round(
        metrics["Total Return %"],
        2,
    )

    metrics["Profit / Trade"] = round(
        safe_divide(
            metrics["Net Profit %"],
            metrics["Trades"],
        ),
        3,
    )

    metrics["Holding Occupancy"] = round(
        safe_divide(
            holding.sum(),
            years * 365.25,
        ),
        3,
    )

    metrics["Annual Holding Days"] = round(
        safe_divide(
            holding.sum(),
            years,
        ),
        2,
    )

    logger.info(
        "Completed summary metrics for %s",
        stock,
    )

    return metrics


# ==========================================================
# Public Exports
# ==========================================================

__all__ += [
    "trade_statistics",
    "holding_statistics",
    "return_statistics",
    "streak_statistics",
    "risk_statistics",
    "exit_statistics",
    "exit_quality",
    "frequency_statistics",
    "capital_efficiency",
    "compute_trade_metrics",
]
