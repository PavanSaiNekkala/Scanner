"""
utils.py
========

Institutional Backtesting Utilities.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# Returns
# ==========================================================


def simple_returns(
    prices: pd.Series,
) -> pd.Series:
    """
    Calculate simple returns.
    """

    return (
        prices
        .pct_change()
        .fillna(0.0)
    )


def log_returns(
    prices: pd.Series,
) -> pd.Series:
    """
    Calculate logarithmic returns.
    """

    return (
        np.log(
            prices
            / prices.shift(1)
        )
        .fillna(0.0)
    )


def cumulative_returns(
    returns: pd.Series,
) -> pd.Series:
    """
    Cumulative return series.
    """

    return (
        (1 + returns)
        .cumprod()
        - 1
    )


# ==========================================================
# Annualization
# ==========================================================


def annualized_return(
    returns: pd.Series,
    periods: int = 252,
) -> float:
    """
    Annualized return.
    """

    compounded = (
        (1 + returns)
        .prod()
    )

    years = (
        len(returns)
        / periods
    )

    if years <= 0:
        return 0.0

    return (
        compounded
        ** (1 / years)
        - 1
    )


def annualized_volatility(
    returns: pd.Series,
    periods: int = 252,
) -> float:
    """
    Annualized volatility.
    """

    return (
        returns.std()
        * np.sqrt(periods)
    )


# ==========================================================
# Statistics
# ==========================================================


def mean(
    values: pd.Series,
) -> float:
    """
    Mean.
    """

    return float(
        values.mean()
    )


def median(
    values: pd.Series,
) -> float:
    """
    Median.
    """

    return float(
        values.median()
    )


def variance(
    values: pd.Series,
) -> float:
    """
    Variance.
    """

    return float(
        values.var()
    )


def standard_deviation(
    values: pd.Series,
) -> float:
    """
    Standard deviation.
    """

    return float(
        values.std()
    )


def downside_deviation(
    returns: pd.Series,
) -> float:
    """
    Downside deviation.
    """

    downside = returns[
        returns < 0
    ]

    if downside.empty:
        return 0.0

    return float(
        downside.std()
    )

# ==========================================================
# Rolling Statistics
# ==========================================================


def rolling_return(
    returns: pd.Series,
    window: int = 252,
) -> pd.Series:
    """
    Rolling cumulative return.
    """

    return (
        (1 + returns)
        .rolling(window)
        .apply(
            np.prod,
            raw=True,
        )
        - 1
    )


def rolling_volatility(
    returns: pd.Series,
    window: int = 252,
    periods: int = 252,
) -> pd.Series:
    """
    Rolling annualized volatility.
    """

    return (
        returns
        .rolling(window)
        .std()
        * np.sqrt(periods)
    )


def rolling_drawdown(
    equity: pd.Series,
    window: int = 252,
) -> pd.Series:
    """
    Rolling drawdown.
    """

    rolling_peak = (
        equity
        .rolling(
            window,
            min_periods=1,
        )
        .max()
    )

    return (
        equity
        / rolling_peak
        - 1
    )


def max_drawdown(
    equity: pd.Series,
) -> float:
    """
    Maximum drawdown.
    """

    peak = equity.cummax()

    drawdown = (
        equity
        / peak
        - 1
    )

    return float(
        drawdown.min()
    )


# ==========================================================
# Ratios
# ==========================================================


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods: int = 252,
) -> float:
    """
    Annualized Sharpe ratio.
    """

    excess = (
        returns
        - risk_free_rate / periods
    )

    volatility = excess.std()

    if volatility == 0:
        return 0.0

    return float(
        np.sqrt(periods)
        * excess.mean()
        / volatility
    )


def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods: int = 252,
) -> float:
    """
    Annualized Sortino ratio.
    """

    excess = (
        returns
        - risk_free_rate / periods
    )

    downside = excess[
        excess < 0
    ]

    if downside.empty:
        return 0.0

    downside_std = downside.std()

    if downside_std == 0:
        return 0.0

    return float(
        np.sqrt(periods)
        * excess.mean()
        / downside_std
    )


def calmar_ratio(
    returns: pd.Series,
    equity: pd.Series,
    periods: int = 252,
) -> float:
    """
    Calmar ratio.
    """

    mdd = abs(
        max_drawdown(
            equity,
        )
    )

    if mdd == 0:
        return 0.0

    return (
        annualized_return(
            returns,
            periods,
        )
        / mdd
    )


# ==========================================================
# Factor Statistics
# ==========================================================


def beta(
    returns: pd.Series,
    benchmark: pd.Series,
) -> float:
    """
    Portfolio beta.
    """

    covariance = np.cov(
        returns,
        benchmark,
    )[0, 1]

    variance = np.var(
        benchmark,
    )

    if variance == 0:
        return 0.0

    return float(
        covariance
        / variance
    )


def alpha(
    returns: pd.Series,
    benchmark: pd.Series,
    risk_free_rate: float = 0.0,
    periods: int = 252,
) -> float:
    """
    Jensen's alpha.
    """

    b = beta(
        returns,
        benchmark,
    )

    portfolio = annualized_return(
        returns,
        periods,
    )

    benchmark_return = annualized_return(
        benchmark,
        periods,
    )

    return (
        portfolio
        - (
            risk_free_rate
            + b
            * (
                benchmark_return
                - risk_free_rate
            )
        )
    )

# ==========================================================
# Correlation & Normalization
# ==========================================================


def correlation(
    x: pd.Series,
    y: pd.Series,
) -> float:
    """
    Pearson correlation.
    """

    return float(
        x.corr(
            y,
        )
    )


def covariance(
    x: pd.Series,
    y: pd.Series,
) -> float:
    """
    Covariance.
    """

    return float(
        x.cov(
            y,
        )
    )


def normalize(
    values: pd.Series,
) -> pd.Series:
    """
    Min-max normalization.
    """

    minimum = values.min()

    maximum = values.max()

    if maximum == minimum:

        return pd.Series(
            0.0,
            index=values.index,
        )

    return (
        values - minimum
    ) / (
        maximum - minimum
    )


def winsorize(
    values: pd.Series,
    lower: float = 0.01,
    upper: float = 0.99,
) -> pd.Series:
    """
    Winsorize a series.
    """

    lower_bound = values.quantile(
        lower,
    )

    upper_bound = values.quantile(
        upper,
    )

    return values.clip(
        lower_bound,
        upper_bound,
    )


def z_score(
    values: pd.Series,
) -> pd.Series:
    """
    Z-score normalization.
    """

    std = values.std()

    if std == 0:

        return pd.Series(
            0.0,
            index=values.index,
        )

    return (
        values
        - values.mean()
    ) / std


# ==========================================================
# Date Utilities
# ==========================================================


def business_days(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp,
) -> int:
    """
    Number of business days.
    """

    return len(
        pd.bdate_range(
            start=start,
            end=end,
        )
    )


def date_range(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp,
    frequency: str = "D",
) -> pd.DatetimeIndex:
    """
    Create a date range.
    """

    return pd.date_range(
        start=start,
        end=end,
        freq=frequency,
    )


# ==========================================================
# Filesystem
# ==========================================================


def ensure_directory(
    path: str | Path,
) -> Path:
    """
    Create a directory if it does not exist.
    """

    directory = Path(
        path,
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory

# ==========================================================
# Formatting
# ==========================================================


def format_currency(
    value: float,
    decimals: int = 2,
    currency: str = "₹",
) -> str:
    """
    Format a currency value.
    """

    return (
        f"{currency}"
        f"{value:,.{decimals}f}"
    )


def format_percentage(
    value: float,
    decimals: int = 2,
) -> str:
    """
    Format percentage.
    """

    return (
        f"{value * 100:.{decimals}f}%"
    )


# ==========================================================
# Numeric Helpers
# ==========================================================


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """
    Safe division.
    """

    if denominator == 0:

        return default

    return numerator / denominator


def clip(
    values: pd.Series,
    lower: float,
    upper: float,
) -> pd.Series:
    """
    Clip values.
    """

    return values.clip(
        lower,
        upper,
    )


# ==========================================================
# Ranking
# ==========================================================


def rank_series(
    values: pd.Series,
    ascending: bool = False,
) -> pd.Series:
    """
    Rank a series.
    """

    return values.rank(
        ascending=ascending,
        method="dense",
    )


def rolling_rank(
    values: pd.Series,
    window: int = 20,
) -> pd.Series:
    """
    Rolling rank.
    """

    return values.rolling(
        window,
    ).apply(
        lambda x: pd.Series(
            x,
        ).rank(
            method="dense",
        ).iloc[-1],
        raw=False,
    )


# ==========================================================
# Conversion
# ==========================================================


def to_dataframe(
    data: dict,
) -> pd.DataFrame:
    """
    Convert dictionary to DataFrame.
    """

    return pd.DataFrame(
        [data],
    )

__all__ = [
    "simple_returns",
    "log_returns",
    "cumulative_returns",
    "annualized_return",
    "annualized_volatility",
    "mean",
    "median",
    "variance",
    "standard_deviation",
    "downside_deviation",
    "rolling_return",
    "rolling_volatility",
    "rolling_drawdown",
    "max_drawdown",
    "sharpe_ratio",
    "sortino_ratio",
    "calmar_ratio",
    "beta",
    "alpha",
    "correlation",
    "covariance",
    "normalize",
    "winsorize",
    "z_score",
    "business_days",
    "date_range",
    "ensure_directory",
    "format_currency",
    "format_percentage",
    "safe_divide",
    "clip",
    "rank_series",
    "rolling_rank",
    "to_dataframe",
]