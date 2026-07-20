"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
portfolio/allocation.py

Purpose
-------
Institutional portfolio allocation engine providing
multiple allocation methodologies with standardized
validation, normalization, and position sizing.

Supported Methods
-----------------
• Equal Weight
• Composite Score
• Edge Score
• Reliability Score
• Blended Allocation

=============================================================
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EDGE_SCORE,
    RELIABILITY_SCORE,
)
from strategy_compare_v4.config.thresholds import (
    MAX_POSITION_WEIGHT,
    MIN_POSITION_WEIGHT,
)
from strategy_compare_v4.utils.helpers import (
    require_columns,
)
from strategy_compare_v4.utils.logger import (
    banner,
    get_logger,
)
from strategy_compare_v4.utils.math_utils import (
    round_dataframe,
    safe_divide,
)

logger = get_logger(__name__)


# ============================================================
# Validation
# ============================================================


def validate_portfolio_input(
    df: pd.DataFrame,
    required_columns: list[str],
) -> pd.DataFrame:
    """
    Validate portfolio input dataframe.
    """

    banner(
        logger,
        "Validating Portfolio Allocation",
    )

    require_columns(
        df,
        required_columns,
    )

    logger.info(
        "Rows             : %d",
        len(df),
    )

    logger.info(
        "Unique Stocks    : %d",
        df["Stock"].nunique(),
    )

    return df.copy()


# ============================================================
# Equal Weight Allocation
# ============================================================


def equal_weight(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Allocate equal weights
    across all securities.
    """

    df = validate_portfolio_input(
        df,
        ["Stock"],
    )

    total_positions = len(df)

    if total_positions == 0:
        df["Weight"] = pd.Series(
            dtype=float,
        )

        logger.warning("No securities available.")

        return df

    df["Weight"] = round(
        100 / total_positions,
        2,
    )

    logger.info("Equal allocation generated.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Composite Score Allocation
# ============================================================


def score_weight(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Allocate using
    Composite Score.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            COMPOSITE_SCORE,
        ],
    )

    scores = df[COMPOSITE_SCORE].clip(
        lower=0,
    )

    total = scores.sum()

    if total <= 0:
        logger.warning("Composite scores sum to zero.")

        return equal_weight(
            df,
        )

    df["Weight"] = (
        safe_divide(
            scores,
            total,
        )
        * 100
    )

    logger.info("Composite allocation generated.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Edge Score Allocation
# ============================================================


def edge_weight(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Allocate portfolio using
    Edge Score.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            EDGE_SCORE,
        ],
    )

    scores = df[EDGE_SCORE].clip(
        lower=0,
    )

    total = scores.sum()

    if total <= 0:
        logger.warning("Edge scores sum to zero.")

        return equal_weight(
            df,
        )

    df["Weight"] = (
        safe_divide(
            scores,
            total,
        )
        * 100
    )

    logger.info("Edge Score allocation generated.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Reliability Score Allocation
# ============================================================


def reliability_weight(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Allocate portfolio using
    Reliability Score.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            RELIABILITY_SCORE,
        ],
    )

    scores = df[RELIABILITY_SCORE].clip(
        lower=0,
    )

    total = scores.sum()

    if total <= 0:
        logger.warning("Reliability scores sum to zero.")

        return equal_weight(
            df,
        )

    df["Weight"] = (
        safe_divide(
            scores,
            total,
        )
        * 100
    )

    logger.info("Reliability allocation generated.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Blended Allocation
# ============================================================


def blended_weight(
    df: pd.DataFrame,
    composite_weight: float = 0.60,
    reliability_weighting: float = 0.40,
) -> pd.DataFrame:
    """
    Allocate portfolio using a
    weighted blend of Composite
    Score and Reliability Score.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            COMPOSITE_SCORE,
            RELIABILITY_SCORE,
        ],
    )

    blended_score = (
        composite_weight * df[COMPOSITE_SCORE]
        + reliability_weighting * df[RELIABILITY_SCORE]
    ).clip(
        lower=0,
    )

    total = blended_score.sum()

    if total <= 0:
        logger.warning("Blended scores sum to zero.")

        return equal_weight(
            df,
        )

    df["Weight"] = (
        safe_divide(
            blended_score,
            total,
        )
        * 100
    )

    logger.info("Blended allocation generated.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Apply Position Limits
# ============================================================


def apply_position_limits(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply minimum and maximum
    position limits and
    re-normalize weights.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            "Weight",
        ],
    )

    df["Weight"] = df["Weight"].clip(
        lower=MIN_POSITION_WEIGHT,
        upper=MAX_POSITION_WEIGHT,
    )

    total = df["Weight"].sum()

    if total <= 0:
        logger.warning("Weight total is zero after applying limits.")

        return equal_weight(
            df,
        )

    df["Weight"] = (
        safe_divide(
            df["Weight"],
            total,
        )
        * 100
    )

    logger.info("Position limits applied.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Finalize Allocation
# ============================================================


def finalize_weights(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Round weights and ensure
    the total allocation
    equals exactly 100%.
    """

    df = validate_portfolio_input(
        df,
        [
            "Stock",
            "Weight",
        ],
    )

    df["Weight"] = df["Weight"].round(
        2,
    )

    difference = round(
        100 - df["Weight"].sum(),
        2,
    )

    if not df.empty:
        largest = df["Weight"].idxmax()

        df.loc[
            largest,
            "Weight",
        ] += difference

    logger.info("Portfolio weights finalized.")

    return round_dataframe(
        df,
        decimals=2,
    )


# ============================================================
# Portfolio Allocation Dispatcher
# ============================================================


def allocate_portfolio(
    df: pd.DataFrame,
    method: str = "composite",
) -> pd.DataFrame:
    """
    Institutional portfolio
    allocation dispatcher.

    Supported Methods
    -----------------
    • equal
    • composite
    • edge
    • reliability
    • blend
    """

    allocation_methods: dict[
        str,
        Callable[[pd.DataFrame], pd.DataFrame],
    ] = {
        "equal": equal_weight,
        "composite": score_weight,
        "edge": edge_weight,
        "reliability": reliability_weight,
        "blend": blended_weight,
    }

    method = method.strip().lower()

    if method not in allocation_methods:
        logger.warning(
            "Unknown allocation method '%s'. Using Composite Score allocation.",
            method,
        )

        method = "composite"

    logger.info(
        "Allocation Method : %s",
        method.title(),
    )

    portfolio = allocation_methods[method](
        df,
    )

    portfolio = apply_position_limits(
        portfolio,
    )

    portfolio = finalize_weights(
        portfolio,
    )

    logger.info("Portfolio allocation completed.")

    logger.info(
        "Total Allocation : %.2f%%",
        portfolio["Weight"].sum(),
    )

    logger.info(
        "Maximum Position : %.2f%%",
        portfolio["Weight"].max(),
    )

    logger.info(
        "Minimum Position : %.2f%%",
        portfolio["Weight"].min(),
    )

    return portfolio
