"""
==============================================================
Institutional Strategy Comparison Platform V5

Summary Metrics Engine

PART 1
-------
Foundation & Risk Utilities

Responsibilities
-----------------
• Validation
• Safe calculations
• Data normalization
• Date handling
• Equity curve
• Drawdown engine

==============================================================
"""

from __future__ import annotations

import logging
from typing import Any

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
# Safe Math Utilities
# ==========================================================


def safe_divide(
    numerator: float,
    denominator: float,
) -> float:
    """
    Safe division.

    Prevents:
    - Zero division
    - Invalid ratios
    """

    if denominator is None:
        return 0.0

    if abs(float(denominator)) < EPSILON:
        return 0.0

    return float(numerator) / float(denominator)


def safe_mean(
    values: pd.Series,
) -> float:

    if values.empty:
        return 0.0

    return float(values.mean())


def safe_median(
    values: pd.Series,
) -> float:

    if values.empty:
        return 0.0

    return float(values.median())


def safe_std(
    values: pd.Series,
) -> float:

    if len(values) < 2:
        return 0.0

    return float(values.std())


def safe_min(
    values: pd.Series,
) -> float:

    if values.empty:
        return 0.0

    return float(values.min())


def safe_max(
    values: pd.Series,
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
    Validate backtest dataframe.
    """

    missing = REQUIRED_COLUMNS.difference(df.columns)

    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")


# ==========================================================
# Numeric Conversion
# ==========================================================


def numeric(
    series: pd.Series,
) -> pd.Series:
    """
    Convert values safely to float.
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
    Find matching column ignoring case.
    """

    normalized = {str(column).strip().lower(): column for column in df.columns}

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def detect_exit_column(
    df: pd.DataFrame,
) -> str | None:

    return find_column(
        df,
        EXIT_COLUMNS,
    )


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
    Calculate actual backtest duration.
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
                0.25,
            )

    holding = numeric(df["days_held"])

    return max(
        holding.sum() / 365.25,
        0.25,
    )


# ==========================================================
# Return Validation
# ==========================================================


def validate_returns(
    returns: pd.Series,
) -> pd.Series:
    """
    Validate trade returns.

    Removes corrupted values.
    """

    returns = numeric(
        returns,
    )

    # impossible bankruptcy loss

    returns = returns[returns > -99]

    extreme = returns.abs() > 200

    if extreme.any():
        logger.warning(
            "Extreme returns detected: %s",
            returns[extreme].tolist(),
        )

    return returns


# ==========================================================
# Equity Curve
# ==========================================================


def build_equity_curve(
    returns: pd.Series,
    initial_capital: float = INITIAL_CAPITAL,
) -> pd.Series:
    """
    Build compounded equity curve.

    Used for:
    - Drawdown
    - Risk metrics
    - Recovery factor
    - CAGR

    Trade returns are compounded sequentially.
    """

    returns = validate_returns(
        returns,
    )

    if returns.empty:
        return pd.Series(
            dtype=float,
        )

    equity = initial_capital * ((1 + returns / 100).cumprod())

    return equity.clip(
        lower=0.01,
    )


# ==========================================================
# Drawdown Engine
# ==========================================================


def running_peak(
    equity: pd.Series,
) -> pd.Series:

    return equity.cummax()


def drawdown_series(
    equity: pd.Series,
) -> pd.Series:
    """
    Percentage drawdown from peak.
    """

    if equity.empty:
        return pd.Series(dtype=float)

    peak = running_peak(
        equity,
    )

    return (equity / peak - 1) * 100


def maximum_drawdown(
    equity: pd.Series,
) -> float:
    """
    Calculate maximum drawdown.

    Formula:

    Drawdown =
    (Equity - Peak Equity)
    / Peak Equity

    Maximum Drawdown =
    Absolute minimum drawdown
    """

    if equity.empty:
        return 0.0


    peak = (
        equity
        .cummax()
    )


    drawdown = (
        equity
        /
        peak
        -
        1
    ) * 100


    return abs(
        drawdown.min()
    )


# ==========================================================
# Trade Statistics
# ==========================================================


def trade_count(
    returns: pd.Series,
) -> int:
    """
    Total executed trades.
    """

    return int(len(returns))


def winning_trades(
    returns: pd.Series,
) -> pd.Series:

    return returns[returns > 0]


def losing_trades(
    returns: pd.Series,
) -> pd.Series:

    return returns[returns < 0]


def win_count(
    returns: pd.Series,
) -> int:

    return int(len(winning_trades(returns)))


def loss_count(
    returns: pd.Series,
) -> int:

    return int(len(losing_trades(returns)))


def win_rate(
    returns: pd.Series,
) -> float:
    """
    Percentage of profitable trades.
    """

    trades = len(returns)

    if trades == 0:
        return 0.0

    return (win_count(returns) / trades) * 100


# ==========================================================
# Average Returns
# ==========================================================


def average_win(
    returns: pd.Series,
) -> float:

    wins = winning_trades(returns)

    return safe_mean(wins)


def average_loss(
    returns: pd.Series,
) -> float:

    losses = losing_trades(returns)

    return abs(safe_mean(losses))


# ==========================================================
# Profit Factor
# ==========================================================


def profit_factor(
    returns: pd.Series,
) -> float:
    """
    Gross profit / Gross loss.

    Institutional definition:

    PF > 1 profitable
    PF > 2 strong
    PF > 5 investigate
    """

    wins = winning_trades(returns)

    losses = losing_trades(returns)

    gross_profit = wins.sum() if not wins.empty else 0.0

    gross_loss = abs(losses.sum())

    if gross_loss <= EPSILON:
        # all winning strategy

        if gross_profit > 0:
            return 10.0

        return 0.0

    return float(gross_profit / gross_loss)


# ==========================================================
# Reward Risk
# ==========================================================


def reward_risk_ratio(
    returns: pd.Series,
) -> float:
    """
    Average reward / average risk.
    """

    avg_win = average_win(returns)

    avg_loss = average_loss(returns)

    return safe_divide(
        avg_win,
        avg_loss,
    )


# ==========================================================
# Expectancy
# ==========================================================


def expectancy(
    returns: pd.Series,
) -> float:
    """
    Expected return per trade.

    Formula:

    (Win% × Avg Win)
    -
    (Loss% × Avg Loss)
    """

    if returns.empty:
        return 0.0

    wins = win_rate(returns) / 100

    losses = loss_count(returns) / len(returns)

    return float((wins * average_win(returns)) - (losses * average_loss(returns)))


# ==========================================================
# Return Distribution
# ==========================================================


def median_return(
    returns: pd.Series,
) -> float:

    return safe_median(returns)


def best_trade(
    returns: pd.Series,
) -> float:

    return safe_max(returns)


def worst_trade(
    returns: pd.Series,
) -> float:

    return safe_min(returns)


def return_std(
    returns: pd.Series,
) -> float:

    return safe_std(returns)


# ==========================================================
# Trade Frequency
# ==========================================================


def trades_per_year(
    trades: int,
    years: float,
) -> float:
    """
    Annual trade frequency.
    """

    if years <= 0:
        return 0.0

    return float(trades / years)


# ==========================================================
# Holding Period
# ==========================================================


def average_holding_days(
    df: pd.DataFrame,
) -> float:

    if "days_held" not in df.columns:
        return 0.0

    values = numeric(df["days_held"])

    return safe_mean(values)


def median_holding_days(
    df: pd.DataFrame,
) -> float:

    if "days_held" not in df.columns:
        return 0.0

    values = numeric(df["days_held"])

    return safe_median(values)


# ==========================================================
# Streak Analysis
# ==========================================================


def longest_streak(
    returns: pd.Series,
    positive: bool = True,
) -> int:
    """
    Longest winning/losing streak.
    """

    if returns.empty:
        return 0

    condition = returns > 0 if positive else returns < 0

    max_streak = 0

    current = 0

    for value in condition:
        if value:
            current += 1

            max_streak = max(
                max_streak,
                current,
            )

        else:
            current = 0

    return int(max_streak)


def consecutive_wins(
    returns: pd.Series,
) -> int:

    return longest_streak(
        returns,
        positive=True,
    )


def consecutive_losses(
    returns: pd.Series,
) -> int:

    return longest_streak(
        returns,
        positive=False,
    )


# ==========================================================
# Trade Quality Summary
# ==========================================================

def trade_quality_statistics(
    returns: pd.Series,
) -> MetricsDict:
    """
    Core trade statistics block.

    Produces:
    - Base trade statistics
    - Institutional metric aliases
    """

    avg_win = average_win(
        returns,
    )

    avg_loss = average_loss(
        returns,
    )

    exp = expectancy(
        returns,
    )

    return {

        "Trades": trade_count(
            returns,
        ),

        "Wins": win_count(
            returns,
        ),

        "Losses": loss_count(
            returns,
        ),


        "Win%": round(
            win_rate(
                returns,
            ),
            2,
        ),


        # -------------------------
        # Average Trade Returns
        # -------------------------

        "Avg Win %": round(
            avg_win,
            2,
        ),

        "Avg Loss %": round(
            avg_loss,
            2,
        ),


        # Compatibility aliases
        # Required by V4 derived metrics

        "Avg win%": round(
            avg_win,
            2,
        ),

        "Avg loss%": round(
            avg_loss,
            2,
        ),


        # -------------------------
        # Edge Metrics
        # -------------------------

        "Profit Factor": round(
            profit_factor(
                returns,
            ),
            3,
        ),

        "Reward Risk": round(
            reward_risk_ratio(
                returns,
            ),
            3,
        ),

        "Expectancy": round(
            exp,
            3,
        ),


        # Compatibility alias

        "Expectancy%": round(
            exp,
            3,
        ),


        # -------------------------
        # Distribution Metrics
        # -------------------------

        "Best Trade %": round(
            best_trade(
                returns,
            ),
            2,
        ),

        "Worst Trade %": round(
            worst_trade(
                returns,
            ),
            2,
        ),

        "Std Return %": round(
            return_std(
                returns,
            ),
            2,
        ),


        # -------------------------
        # Streak Metrics
        # -------------------------

        "Winning Streak": consecutive_wins(
            returns,
        ),

        "Losing Streak": consecutive_losses(
            returns,
        ),
    }

def annual_statistics(
    returns: pd.Series,
    years: float,
) -> MetricsDict:
    """
    Annual return statistics.

    Produces:
    - Total Return %
    - Net %
    - Annual Return %
    - CAGR %
    """

    if returns.empty:
        return {
            "Net %": 0.0,
            "Total Return %": 0.0,
            "Annual Return %": 0.0,
            "CAGR %": 0.0,
        }


    equity = build_equity_curve(
        returns,
    )


    if equity.empty:
        return {
            "Net %": 0.0,
            "Total Return %": 0.0,
            "Annual Return %": 0.0,
            "CAGR %": 0.0,
        }


    final_equity = equity.iloc[-1]


    total_return = (
        final_equity
        /
        INITIAL_CAPITAL
        -
        1
    ) * 100


    if years <= 0:

        annual_return = 0.0

        cagr = 0.0

    else:

        annual_return = (
            total_return
            /
            years
        )


        cagr = (
            (
                final_equity
                /
                INITIAL_CAPITAL
            )
            **
            (
                1
                /
                years
            )
            -
            1
        ) * 100
        

    net_return = returns.sum()

    return {

        # Compatibility field

        "Net %": round(
            net_return,
            2,
        ),


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
# Sharpe Ratio
# ==========================================================


def sharpe_ratio(
    returns: pd.Series,
    years: float,
    risk_free_rate: float = 0.0,
) -> float:
    """
    Trade frequency annualized Sharpe.

    Note:
    Uses trade observations.
    """

    if len(returns) < 2:
        return 0.0

    if years <= 0:
        return 0.0

    excess = returns - risk_free_rate

    volatility = excess.std()

    if abs(volatility) < EPSILON:
        return 0.0

    annual_factor = np.sqrt(252)

    return float(
        (excess.mean() / volatility)
        *
        annual_factor
    )


# ==========================================================
# Sortino Ratio
# ==========================================================


def sortino_ratio(
    returns: pd.Series,
    years: float,
    target_return: float = 0.0,
) -> float:
    """
    Annualized trade-based Sortino Ratio.

    Uses downside deviation only.
    """

    if len(returns) < 2:
        return 0.0

    if years <= 0:
        return 0.0

    downside = returns[returns < target_return]

    # insufficient downside observations
    if len(downside) < 5:
        return 0.0

    downside_std = downside.std()

    if abs(downside_std) < EPSILON:
        return 0.0

    annual_factor = np.sqrt(252)

    return float(
        ((returns.mean() - target_return)
        / downside_std)
        *
        annual_factor
    )


# ==========================================================
# Recovery Factor
# ==========================================================


def recovery_factor(
    equity: pd.Series,
) -> float:
    """
    Net Profit / Maximum Drawdown.
    """

    if equity.empty:
        return 0.0

    net_profit = (
        equity.iloc[-1]
        -
        INITIAL_CAPITAL
    )

    mdd = maximum_drawdown(
        equity,
    )

    return safe_divide(
        net_profit,
        mdd,
    )

# ==========================================================
# Calmar Ratio
# ==========================================================


def calmar_ratio(
    cagr: float,
    equity: pd.Series,
) -> float:
    """
    CAGR / Maximum Drawdown.
    """

    mdd = maximum_drawdown(
        equity,
    )

    if mdd <= EPSILON:
        return 0.0

    return safe_divide(
        cagr,
        mdd,
    )


# ==========================================================
# MAR Ratio
# ==========================================================


def mar_ratio(
    cagr: float,
    equity: pd.Series,
) -> float:
    """
    Same concept as Calmar.

    CAGR divided by maximum drawdown.
    """

    return calmar_ratio(
        cagr,
        equity,
    )


# ==========================================================
# Ulcer Index
# ==========================================================


def ulcer_index(
    equity: pd.Series,
) -> float:
    """
    Measures depth and duration of drawdowns.
    """

    if equity.empty:
        return 0.0

    dd = drawdown_series(
        equity,
    )

    return float(np.sqrt(np.mean(dd**2)))


# ==========================================================
# Omega Ratio
# ==========================================================


def omega_ratio(
    returns: pd.Series,
    threshold: float = 0.0,
) -> float:
    """
    Probability weighted return ratio.

    Gain / Loss.
    """

    gains = returns[returns > threshold]

    losses = returns[returns < threshold]

    positive = gains.sum()

    negative = abs(losses.sum())

    if negative <= EPSILON:
        return 0.0

    return safe_divide(
        positive,
        negative,
    )


# ==========================================================
# Risk Statistics
# ==========================================================


def risk_statistics(
    returns: pd.Series,
    years: float,
) -> MetricsDict:
    """
    Complete institutional risk block.
    """

    equity = build_equity_curve(
        returns,
    )

    annual = annual_statistics(
        returns,
        years,
    )

    cagr = annual.get(
        "CAGR %",
        0.0,
    )

    return {
        **annual,
        "Max Drawdown %": round(
            maximum_drawdown(
                equity,
            ),
            2,
        ),
        "Sharpe": round(
            sharpe_ratio(
                returns,
                years,
            ),
            3,
        ),
        "Sortino": round(
            sortino_ratio(
                returns,
                years,
            ),
            3,
        ),
        "Recovery Factor": round(
            recovery_factor(
                equity,
            ),
            3,
        ),
        "Calmar": round(
            calmar_ratio(
                cagr,
                equity,
            ),
            3,
        ),
        "MAR": round(
            mar_ratio(
                cagr,
                equity,
            ),
            3,
        ),
        "Ulcer Index": round(
            ulcer_index(
                equity,
            ),
            3,
        ),
        "Omega": round(
            omega_ratio(
                returns,
            ),
            3,
        ),
    }


# ==========================================================
# Exit Analytics
# ==========================================================


def detect_exit_reason(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Detect exit reason column.
    """

    column = detect_exit_column(
        df,
    )

    if column is None:
        return pd.Series(
            "Unknown",
            index=df.index,
        )

    return df[column].astype(str).str.strip()


def exit_statistics(
    df: pd.DataFrame,
) -> MetricsDict:
    """
    Exit quality analysis.

    Generates:
    - Exit distribution
    - Institutional compatibility fields
    """

    exits = detect_exit_reason(
        df,
    )

    total = len(
        exits,
    )


    if total == 0:

        return {

            "Target #": 0,

            "Trail #": 0,

            "Stop #": 0,

            "Time #": 0,


            "Target Exit %": 0.0,

            "Trailing Exit %": 0.0,

            "Stop Exit %": 0.0,

            "Time Exit %": 0.0,

        }


    normalized = exits.str.lower()


    target = normalized.str.contains(
        "target",
    ).sum()


    stop = normalized.str.contains(
        "stop",
    ).sum()


    trail = normalized.str.contains(
        "trail",
    ).sum()


    time_exit = normalized.str.contains(
        "time",
    ).sum()


    target_pct = (
        target / total
    ) * 100


    trail_pct = (
        trail / total
    ) * 100


    stop_pct = (
        stop / total
    ) * 100


    time_pct = (
        time_exit / total
    ) * 100


    return {

        "Target #": int(
            target,
        ),

        "Trail #": int(
            trail,
        ),

        "Stop #": int(
            stop,
        ),

        "Time #": int(
            time_exit,
        ),


        # Existing V5 naming

        "Target %": round(
            target_pct,
            2,
        ),

        "Trail %": round(
            trail_pct,
            2,
        ),

        "Stop %": round(
            stop_pct,
            2,
        ),

        "Time %": round(
            time_pct,
            2,
        ),


        # V4/V5 compatibility naming

        "Target Exit %": round(
            target_pct,
            2,
        ),

        "Trailing Exit %": round(
            trail_pct,
            2,
        ),

        "Stop Exit %": round(
            stop_pct,
            2,
        ),

        "Time Exit %": round(
            time_pct,
            2,
        ),
    }

# ==========================================================
# Efficiency Metrics
# ==========================================================

def holding_efficiency(
    returns: pd.Series,
    days: pd.Series,
) -> float:
    """
    Return generated per holding day.

    Formula:

    Average Trade Return
    --------------------
    Average Holding Days
    """

    if returns.empty:
        return 0.0


    avg_days = safe_mean(
        days,
    )


    if avg_days <= 0:
        return 0.0


    avg_return = safe_mean(
        returns,
    )


    return safe_divide(
        avg_return,
        avg_days,
    )


# ==========================================================
# Opportunity Metrics
# ==========================================================

def opportunity_score(
    returns: pd.Series,
) -> float:
    """
    Institutional opportunity score.

    Components:

    Trade Capacity       40%
    Expectancy Quality   35%
    Win Reliability      25%

    Output:

    0 - 100
    """

    if returns.empty:
        return 0.0


    trade_capacity = min(
        len(returns) / 500,
        1.0,
    )


    expectancy_value = expectancy(
        returns,
    )


    expectancy_quality = min(
        max(
            expectancy_value / 10,
            0,
        ),
        1,
    )


    win_quality = (
        win_rate(
            returns,
        )
        /
        100
    )


    score = (

        trade_capacity * 40

        +

        expectancy_quality * 35

        +

        win_quality * 25

    )


    return round(
        float(score),
        2,
    )

def trade_velocity(
    trades: int,
    years: float,
) -> float:
    """
    Annual trade frequency.

    Formula:

    Trades / Years
    """

    if years <= 0:
        return 0.0

    return safe_divide(
        trades,
        years,
    )

def capital_efficiency(
    cagr: float,
    max_drawdown: float,
) -> float:
    """
    Risk adjusted capital efficiency.

    Formula:

    CAGR / Max Drawdown

    Equivalent to Calmar Ratio.
    """

    return safe_divide(
        cagr,
        abs(max_drawdown),
    )

# ==========================================================
# Final Metrics Engine
# ==========================================================

def compute_trade_metrics(
    stock: str,
    df: pd.DataFrame,
) -> MetricsDict:
    """
    Complete institutional metric calculation.

    Flow:

    Trade Data
        ↓
    Base Statistics
        ↓
    Performance Metrics
        ↓
    Risk Metrics
        ↓
    Efficiency Metrics
        ↓
    Opportunity Metrics

    """

    validate_trade_dataframe(
        df,
    )

    returns = validate_returns(
        numeric(
            df["net_return_%"]
        )
    )

    years = calculate_calendar_years(
        df,
    )

    days = numeric(
        df["days_held"]
    )

    trades = len(
        returns,
    )

    risk = risk_statistics(
        returns,
        years,
    )

    trade_quality = trade_quality_statistics(
        returns,
    )

    exits = exit_statistics(
        df,
    )

    max_dd = risk.get(
        "Max Drawdown %",
        0.0,
    )

    cagr = risk.get(
        "CAGR %",
        0.0,
    )

    net_return = risk.get(
        "Net %",
        0.0,
    )

    total_return = risk.get(
        "Net %",
        0.0,
    )


    return {

        # -------------------------
        # Identity
        # -------------------------

        "Stock": stock,


        # -------------------------
        # Duration
        # -------------------------

        "Years": round(
            years,
            2,
        ),


        "Avg days": round(
            safe_mean(days),
            2,
        ),


        # -------------------------
        # Trade Statistics
        # -------------------------

        **trade_quality,


        # -------------------------
        # Performance Metrics
        # -------------------------

        "Net %": round(
            net_return,
            2,
        ),


        "Total Return %": round(
            total_return,
            2,
        ),


        "Annual Return %": risk.get(
            "Annual Return %",
            0.0,
        ),


        "CAGR %": round(
            cagr,
            2,
        ),


        # -------------------------
        # Risk Metrics
        # -------------------------

        **risk,


        # -------------------------
        # Exit Metrics
        # -------------------------

        **exits,


        # -------------------------
        # Efficiency Metrics
        # -------------------------

        "Trades / Year": round(
            trade_velocity(
                trades,
                years,
            ),
            2,
        ),


        "Holding Efficiency": round(
            holding_efficiency(
                returns,
                days,
            ),
            4,
        ),


        "Capital Efficiency": round(
            capital_efficiency(
                cagr,
                max_dd,
            ),
            3,
        ),


        # -------------------------
        # Opportunity Metrics
        # -------------------------

        "Opportunity Score": round(
            opportunity_score(
                returns,
            ),
            2,
        ),
    }


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


    "validate_trade_dataframe",

    "validate_returns",


    "calculate_calendar_years",


    "build_equity_curve",

    "drawdown_series",

    "maximum_drawdown",


    "trade_quality_statistics",


    "profit_factor",

    "reward_risk_ratio",

    "expectancy",


    "annual_statistics",

    "risk_statistics",


    "sharpe_ratio",

    "sortino_ratio",

    "recovery_factor",

    "calmar_ratio",

    "mar_ratio",


    "exit_statistics",


    "holding_efficiency",

    "capital_efficiency",

    "trade_velocity",


    "opportunity_score",


    "compute_trade_metrics",

]