"""
metrics_service.py
==================

Institutional Metrics Engine

Computes derived analytics from the scanner universe.

Responsibilities
----------------
• Opportunity Metrics
• Risk Metrics
• Trend Metrics
• Momentum Metrics
• Volume Metrics
• Ranking Metrics
• Composite Scores
• Recommendation Inputs
• Metric Normalization
• Percentile Ranking
• Data Validation

This module contains no Streamlit dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

import logging
import math

import numpy as np
import pandas as pd

# =============================================================================
# Logger
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass(frozen=True)
class MetricsConfig:
    """
    Configuration for institutional metric calculations.
    """

    # ---------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------

    normalization_min: float = 0.0
    normalization_max: float = 100.0
    percentile_method: str = "average"
    clip_scores: bool = True

    # ---------------------------------------------------------
    # Numerical Stability
    # ---------------------------------------------------------

    epsilon: float = 1e-12
    infinite_replacement: float = np.nan

    # ---------------------------------------------------------
    # Composite Score Weights
    # ---------------------------------------------------------

    opportunity_weight: float = 0.20
    risk_weight: float = 0.20
    trend_weight: float = 0.15
    momentum_weight: float = 0.15
    volume_weight: float = 0.10
    ranking_weight: float = 0.20

    # ---------------------------------------------------------
    # Composite Engine Weights
    # ---------------------------------------------------------

    institutional_weight: float = 0.35
    alpha_weight: float = 0.25
    execution_weight: float = 0.20
    portfolio_weight: float = 0.20

    # ---------------------------------------------------------
    # Alpha Score Weights
    # ---------------------------------------------------------

    alpha_opportunity_weight: float = 0.45
    alpha_trend_weight: float = 0.30
    alpha_momentum_weight: float = 0.25

    # ---------------------------------------------------------
    # Execution Score Weights
    # ---------------------------------------------------------

    execution_volume_weight: float = 0.40
    execution_risk_weight: float = 0.30
    execution_liquidity_weight: float = 0.15
    execution_confidence_weight: float = 0.15

    # ---------------------------------------------------------
    # Portfolio Fit Weights
    # ---------------------------------------------------------

    portfolio_quality_weight: float = 0.40
    portfolio_risk_weight: float = 0.30
    portfolio_opportunity_weight: float = 0.30

    # ---------------------------------------------------------
    # Recommendation Score Weights
    # ---------------------------------------------------------

    recommendation_composite_weight: float = 0.50
    recommendation_quality_weight: float = 0.20
    recommendation_opportunity_weight: float = 0.15
    recommendation_risk_weight: float = 0.15

    # ---------------------------------------------------------
    # Thresholds
    # ---------------------------------------------------------

    minimum_confidence: float = 0.0
    minimum_rr: float = 0.0
    minimum_volume_ratio: float = 0.0

    # ---------------------------------------------------------
    # Misc
    # ---------------------------------------------------------

    rounding_digits: int = 4
    copy_dataframe: bool = True


# =============================================================================
# Statistics
# =============================================================================

@dataclass
class MetricStatistics:
    """
    Summary statistics for calculated metrics.
    """

    total_rows: int = 0

    calculated_metrics: int = 0

    skipped_metrics: int = 0

    failed_metrics: int = 0

    missing_columns: list[str] = field(
        default_factory=list,
    )

    warnings: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# Result Model
# =============================================================================

@dataclass
class MetricsResult:
    """
    Result returned by MetricsService.
    """

    dataframe: pd.DataFrame

    statistics: MetricStatistics

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# =============================================================================
# Canonical Scanner Columns
# =============================================================================

class ScannerColumns:
    """
    Canonical scanner column names.

    Keeping all column names centralized avoids
    hardcoding literals throughout the service.
    """

    TICKER = "ticker"
    COMPANY = "company"
    SECTOR = "sector"
    SUBSECTOR = "subsector"
    EXCHANGE = "exchange"
    STRATEGY = "strategy"
    RECOMMENDATION = "recommendation"
    SIGNALS = "signals_today"
    CONFIDENCE = "confidence"
    RANK_SCORE = "rank_score"
    PORTFOLIO_RANK = "portfolio_rank"
    REGIME = "regime_today"
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    CMP = "cmp"
    VOLUME = "volume"
    ENTRY = "entry"
    TARGET = "target"
    STOP = "stop_loss"
    HOLD_DAYS = "target_hold_days"
    EXPECTED_RETURN_PCT = "expected_return_pct"
    EXPECTED_RETURN_POINTS = "expected_return_points"
    RISK_PCT = "risk_pct"
    RISK_POINTS = "risk_points"
    RISK_REWARD = "risk_reward"
    ATR_PCT = "atr_pct"
    RSI = "rsi"
    ROC = "roc"
    VOLUME_RATIO = "volume_ratio"
    ABOVE_50DMA = "above_50dma"
    ABOVE_200DMA = "above_200dma"
    TRADE_STATUS = "trade_status"
    REMARKS = "remarks"


# =============================================================================
# Derived Metric Columns
# =============================================================================

class MetricColumns:
    """
    Canonical names for all derived metrics.

    Every calculated column produced by MetricsService should
    be referenced through this registry instead of string
    literals.
    """

    # -----------------------------------------------------------------
    # Opportunity
    # -----------------------------------------------------------------

    REMAINING_UPSIDE_PCT = "remaining_upside_pct"
    ENTRY_DISTANCE_PCT = "entry_distance_pct"
    TARGET_COMPLETION_PCT = "target_completion_pct"
    RETURN_PER_DAY_PCT = "return_per_day_pct"
    RISK_PER_DAY_PCT = "risk_per_day_pct"
    CAPITAL_EFFICIENCY = "capital_efficiency"
    OPPORTUNITY_EFFICIENCY = "opportunity_efficiency"
    CONFIDENCE_WEIGHTED_RETURN = "confidence_weighted_return"
    ATR_ADJUSTED_RETURN = "atr_adjusted_return"
    STOP_CUSHION_PCT = "stop_cushion_pct"
    OPPORTUNITY_SCORE = "opportunity_score"

    # -----------------------------------------------------------------
    # Risk
    # -----------------------------------------------------------------

    DOWNSIDE_EXPOSURE_PCT = "downside_exposure_pct"
    TARGET_STOP_DISTANCE_RATIO = "target_stop_distance_ratio"
    ATR_RISK_MULTIPLE = "atr_risk_multiple"
    RETURN_TO_ATR_RATIO = "return_to_atr_ratio"
    RISK_ADJUSTED_RETURN = "risk_adjusted_return"
    VOLATILITY_EFFICIENCY = "volatility_efficiency"
    STOP_LOSS_BUFFER = "stop_loss_buffer"
    RECOVERY_FACTOR = "recovery_factor"
    RISK_SCORE = "risk_score"

    # -----------------------------------------------------------------
    # Trend
    # -----------------------------------------------------------------

    TREND_ALIGNMENT = "trend_alignment"
    TREND_STRENGTH = "trend_strength"
    MOMENTUM_TREND_RATIO = "momentum_trend_ratio"
    RSI_TREND_SCORE = "rsi_trend_score"
    BREAKOUT_STRENGTH = "breakout_strength"
    TREND_CONVICTION = "trend_conviction"
    TREND_SCORE = "trend_score"

    # -----------------------------------------------------------------
    # Momentum
    # -----------------------------------------------------------------

    ROC_STRENGTH = "roc_strength"
    RSI_STRENGTH = "rsi_strength"
    MOMENTUM_ACCELERATION = "momentum_acceleration"
    MOMENTUM_PERSISTENCE = "momentum_persistence"
    RELATIVE_MOMENTUM = "relative_momentum"
    MOMENTUM_EFFICIENCY = "momentum_efficiency"
    CONVICTION_MOMENTUM = "conviction_momentum"
    MOMENTUM_QUALITY = "momentum_quality"
    MOMENTUM_SCORE = "momentum_score"

    # -----------------------------------------------------------------
    # Volume
    # -----------------------------------------------------------------

    VOLUME_STRENGTH = "volume_strength"
    LIQUIDITY_SCORE = "liquidity_score"
    PARTICIPATION_SCORE = "participation_score"
    VOLUME_CONVICTION = "volume_conviction"
    VOLUME_EFFICIENCY = "volume_efficiency"
    LIQUIDITY_EFFICIENCY = "liquidity_efficiency"
    INSTITUTIONAL_PARTICIPATION = "institutional_participation"
    ACCUMULATION_SCORE = "accumulation_score"
    DISTRIBUTION_RISK = "distribution_risk"
    TURNOVER_QUALITY = "turnover_quality"
    VOLUME_SCORE = "volume_score"

    # -----------------------------------------------------------------
    # Quality
    # -----------------------------------------------------------------

    CONFIDENCE_QUALITY = "confidence_quality"
    REWARD_QUALITY = "reward_quality"
    RISK_QUALITY = "risk_quality"
    TREND_QUALITY = "trend_quality"
    LIQUIDITY_QUALITY = "liquidity_quality"
    STABILITY_QUALITY = "stability_quality"
    CONSISTENCY_QUALITY = "consistency_quality"
    OPPORTUNITY_QUALITY = "opportunity_quality"
    QUALITY_SCORE = "quality_score"
    # -----------------------------------------------------------------
    # Composite
    # -----------------------------------------------------------------

    INSTITUTIONAL_SCORE = "institutional_score"
    ALPHA_SCORE = "alpha_score"
    EXECUTION_SCORE = "execution_score"
    PORTFOLIO_FIT_SCORE = "portfolio_fit_score"
    COMPOSITE_SCORE = "composite_score"

    INSTITUTIONAL_GRADE = "institutional_grade"
    TOP_DECILE = "top_decile"
    TOP_QUINTILE = "top_quintile"
    TOP_10_PERCENT = "top_10_percent"
    BOTTOM_10_PERCENT = "bottom_10_percent"

    INSTITUTIONAL_RANK = "institutional_rank"
    INSTITUTIONAL_PERCENTILE = "institutional_percentile"
    INSTITUTIONAL_QUINTILE = "institutional_quintile"
    INSTITUTIONAL_DECILE = "institutional_decile"

    RECOMMENDATION_SCORE = "recommendation_score"
    RECOMMENDATION_BAND = "recommendation_band"

# =============================================================================
# Required Columns
# =============================================================================

REQUIRED_COLUMNS: tuple[str, ...] = (
    ScannerColumns.CMP,
    ScannerColumns.ENTRY,
    ScannerColumns.TARGET,
    ScannerColumns.STOP,
    ScannerColumns.HOLD_DAYS,
    ScannerColumns.EXPECTED_RETURN_PCT,
    ScannerColumns.EXPECTED_RETURN_POINTS,
    ScannerColumns.RISK_PCT,
    ScannerColumns.RISK_POINTS,
    ScannerColumns.RISK_REWARD,
    ScannerColumns.ATR_PCT,
    ScannerColumns.RSI,
    ScannerColumns.ROC,
    ScannerColumns.VOLUME_RATIO,
    ScannerColumns.CONFIDENCE,
)

# =============================================================================
# Utility Functions
# =============================================================================

def _safe_divide(
    numerator: pd.Series | float | np.ndarray,
    denominator: pd.Series | float | np.ndarray,
    *,
    fill_value: float = np.nan,
    epsilon: float = 1e-12,
):
    """
    Safe element-wise division.

    Prevents divide-by-zero and suppresses NumPy warnings.

    Returns
    -------
    Same type as the broadcasted operation.
    """

    with np.errstate(
        divide="ignore",
        invalid="ignore",
    ):

        result = np.divide(
            numerator,
            denominator,
        )

    if isinstance(result, np.ndarray):

        result = np.where(
            np.abs(denominator) <= epsilon,
            fill_value,
            result,
        )

        result = np.where(
            np.isfinite(result),
            result,
            fill_value,
        )

        return result

    if isinstance(result, pd.Series):

        if np.isscalar(denominator):

            if abs(float(denominator)) <= epsilon:

                result = pd.Series(
                    fill_value,
                    index=result.index,
                    dtype=float,
                )

        else:

            if isinstance(
                denominator,
                pd.Series,
            ):

                mask = denominator.reindex(
                    result.index,
                ).abs() <= epsilon

            else:

                mask = (
                    pd.Series(
                        denominator,
                        index=result.index,
                    ).abs()
                    <= epsilon
                )

            result = result.mask(
                mask,
                fill_value,
            )

        result = result.replace(
            [
                np.inf,
                -np.inf,
            ],
            fill_value,
        )

        return result


def _safe_percentage(
    numerator,
    denominator,
) -> pd.Series:
    """
    Safe percentage calculation.

    Computes

        numerator / denominator * 100
    """

    return (
        _safe_divide(
            numerator,
            denominator,
        )
        * 100.0
    )


def _safe_difference(
    lhs,
    rhs,
):
    """
    Difference preserving NaN.
    """

    return pd.to_numeric(
        lhs,
        errors="coerce",
    ) - pd.to_numeric(
        rhs,
        errors="coerce",
    )


def _safe_clip(
    values,
    lower=None,
    upper=None,
):
    """
    Clip numeric values.
    """

    if isinstance(
        values,
        pd.Series,
    ):

        return values.clip(
            lower=lower,
            upper=upper,
        )

    return np.clip(
        values,
        lower,
        upper,
    )


def _round(
    values,
    digits: int = 2,
):
    """
    Consistent rounding helper.
    """

    if isinstance(
        values,
        pd.Series,
    ):

        return values.round(
            digits,
        )

    if isinstance(
        values,
        np.ndarray,
    ):

        return np.round(
            values,
            digits,
        )

    if pd.isna(values):

        return np.nan

    return round(
        float(values),
        digits,
    )


# =============================================================================
# Validation Helpers
# =============================================================================

def _validate_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Validate scanner dataframe.
    """

    if df.empty:

        raise ValueError(
            "Scanner dataframe is empty."
        )

    missing = [

        column

        for column in REQUIRED_COLUMNS

        if column not in df.columns

    ]

    if missing:

        raise ValueError(

            "Missing required columns: "

            + ", ".join(
                missing,
            )

        )


def _coerce_numeric(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert numeric columns to float.
    """

    df = df.copy()

    numeric_columns = [

        ScannerColumns.CMP,
        ScannerColumns.ENTRY,
        ScannerColumns.TARGET,
        ScannerColumns.STOP,
        ScannerColumns.HOLD_DAYS,
        ScannerColumns.EXPECTED_RETURN_PCT,
        ScannerColumns.EXPECTED_RETURN_POINTS,
        ScannerColumns.RISK_PCT,
        ScannerColumns.RISK_POINTS,
        ScannerColumns.RISK_REWARD,
        ScannerColumns.ATR_PCT,
        ScannerColumns.RSI,
        ScannerColumns.ROC,
        ScannerColumns.VOLUME_RATIO,
        ScannerColumns.CONFIDENCE,
        ScannerColumns.RANK_SCORE,
        ScannerColumns.PORTFOLIO_RANK,
        ScannerColumns.OPEN,
        ScannerColumns.HIGH,
        ScannerColumns.LOW,
        ScannerColumns.CLOSE,
        ScannerColumns.VOLUME,
    ]

    for column in numeric_columns:

        if column not in df.columns:
            continue

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    return df


def _validate_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicate securities.
    """

    if (
        ScannerColumns.TICKER
        not in df.columns
    ):

        return df

    return (
        df.drop_duplicates(
            subset=ScannerColumns.TICKER,
            keep="last",
        )
        .reset_index(
            drop=True,
        )
    )


def _validate_boolean_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize boolean scanner columns.
    """

    df = df.copy()

    boolean_columns = [

        ScannerColumns.SIGNALS,
        ScannerColumns.ABOVE_50DMA,
        ScannerColumns.ABOVE_200DMA,

    ]

    for column in boolean_columns:

        if column not in df.columns:

            continue

        df[column] = (
            df[column]
            .fillna(False)
            .astype(bool)
        )

    return df


# =============================================================================
# Data Preparation
# =============================================================================

def _prepare_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Complete preprocessing pipeline.
    """

    _validate_dataframe(
        df,
    )

    df = _coerce_numeric(
        df,
    )

    df = _validate_duplicates(
        df,
    )

    df = _validate_boolean_columns(
        df,
    )

    logger.info(
        "Prepared %d securities for metric calculation.",
        len(df),
    )

    return df

# =============================================================================
# Normalization Engine
# =============================================================================

def _min_max_scale(
    values: pd.Series,
    *,
    lower: float = 0.0,
    upper: float = 100.0,
) -> pd.Series:
    """
    Min-Max normalization.

    Returns
    -------
    Values scaled between lower and upper.
    """

    values = pd.to_numeric(
        values,
        errors="coerce",
    )

    minimum = values.min(skipna=True)
    maximum = values.max(skipna=True)

    if (
        pd.isna(minimum)
        or pd.isna(maximum)
        or np.isclose(
            minimum,
            maximum,
        )
    ):

        return pd.Series(
            lower,
            index=values.index,
            dtype=float,
        )

    scaled = (
        (values - minimum)
        /
        (maximum - minimum)
    )

    return (
        scaled
        * (upper - lower)
        + lower
    )


def _zscore(
    values: pd.Series,
) -> pd.Series:
    """
    Standard score normalization.
    """

    values = pd.to_numeric(
        values,
        errors="coerce",
    )

    mean = values.mean()

    std = values.std(
        ddof=0,
    )

    if (
        pd.isna(std)
        or np.isclose(std, 0.0)
    ):

        return pd.Series(
            0.0,
            index=values.index,
        )

    return (
        values - mean
    ) / std


def _percentile_rank(
    values: pd.Series,
) -> pd.Series:
    """
    Percentile ranking.

    Returns
    -------
    0-100 percentile score.
    """

    values = pd.to_numeric(
        values,
        errors="coerce",
    )

    return (
        values.rank(
            pct=True,
            method="average",
        )
        * 100
    )


def _winsorize(
    values: pd.Series,
    *,
    lower: float = 0.01,
    upper: float = 0.99,
) -> pd.Series:
    """
    Winsorize extreme outliers.
    """

    values = pd.to_numeric(
        values,
        errors="coerce",
    )

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


def _normalize(
    values: pd.Series,
    *,
    higher_is_better: bool = True,
) -> pd.Series:
    """
    Institutional normalization.

    Pipeline
    --------
    Winsorize
        ↓
    Min-Max Scale
        ↓
    0-100 Score
    """

    values = _winsorize(
        values,
    )

    scores = _min_max_scale(
        values,
    )

    if not higher_is_better:

        scores = 100.0 - scores

    return scores.round(2)


# =============================================================================
# Composite Score Helpers
# =============================================================================

def _weighted_score(
    components: dict[
        str,
        tuple[
            pd.Series,
            float,
        ],
    ],
    *,
    normalize: bool = False,
    clip: bool = True,
) -> pd.Series:
    """
    Calculate weighted composite score.

    Parameters
    ----------
    components
        Dictionary of:

        {
            metric_name:
                (
                    values,
                    weight,
                )
        }

    normalize
        Normalize each component before weighting.

        True
            Raw metrics

        False
            Already normalized scores.

    clip
        Clip final score to 0-100.
    """

    weighted_sum = None

    total_weight = 0.0

    for values, weight in components.values():

        values = pd.to_numeric(
            values,
            errors="coerce",
        )

        if normalize:

            values = _normalize(
                values,
            )

        contribution = values * weight

        if weighted_sum is None:

            weighted_sum = contribution

        else:

            weighted_sum += contribution

        total_weight += weight

    if weighted_sum is None:

        return pd.Series(
            dtype=float,
        )

    score = weighted_sum / max(
        total_weight,
        1e-12,
    )

    score = (
        score
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )

    if clip:
        score = score.clip(
            lower=0.0,
            upper=100.0,
        )

    return score.round(2)


def _score_band(
    score: pd.Series,
) -> pd.Series:
    """
    Institutional quality bands.
    """

    return pd.cut(
        score,
        bins=[
            -np.inf,
            20,
            40,
            60,
            80,
            np.inf,
        ],
        labels=[
            "Very Weak",
            "Weak",
            "Average",
            "Strong",
            "Excellent",
        ],
    )


def _quintile(
    values: pd.Series,
) -> pd.Series:
    """
    Quintile classification.

    Returns
    -------
    Integer 1-5.
    """

    values = pd.to_numeric(
        values,
        errors="coerce",
    )

    ranked = values.rank(
        pct=True,
        method="average",
    )

    return (
        np.ceil(
            ranked * 5
        )
        .clip(1, 5)
        .astype("Int64")
    )


def _decile(
    values: pd.Series,
) -> pd.Series:
    """
    Decile classification.
    """

    ranked = values.rank(
        pct=True,
        method="average",
    )

    return (
        np.ceil(
            ranked * 10
        )
        .clip(1, 10)
        .astype("Int64")
    )


def _top_percent(
    values: pd.Series,
    *,
    percent: float = 10.0,
) -> pd.Series:
    """
    Flag top performers.
    """

    threshold = values.quantile(
        1.0 - percent / 100.0,
    )

    return values >= threshold


def _bottom_percent(
    values: pd.Series,
    *,
    percent: float = 10.0,
) -> pd.Series:
    """
    Flag weakest performers.
    """

    threshold = values.quantile(
        percent / 100.0,
    )

    return values <= threshold

# =============================================================================
# Metrics Service
# =============================================================================

MetricCalculator = Callable[
    [pd.DataFrame],
    pd.DataFrame,
]

class MetricsService:
    """
    Institutional metrics engine.

    This service computes all derived analytics used by the
    scanner, reports and dashboard.

    Processing Pipeline
    -------------------
    Validation
            ↓
    Data Preparation
            ↓
    Metric Groups
            ↓
    Composite Scores
            ↓
    Statistics
            ↓
    Result
    """

    def __init__(
        self,
        config: MetricsConfig | None = None,
    ) -> None:

        self.config = config or MetricsConfig()

        self._validate_configuration()

        self.statistics = MetricStatistics()

        self._metric_groups: list[MetricCalculator] = []

        self.register(
            self._calculate_opportunity_metrics,
        )

        self.register(
            self._calculate_risk_metrics,
        )

        self.register(
            self._calculate_trend_metrics,
        )

        self.register(
            self._calculate_momentum_metrics,
        )

        self.register(
            self._calculate_volume_metrics,
        )

        self.register(
            self._calculate_quality_metrics,
        )

        self.register(
            self._calculate_composite_metrics,
        )
      
        logger.info(
            "MetricsService initialized."
        )

    # -------------------------------------------------------------------------
    # Configuration Validation
    # -------------------------------------------------------------------------

    def _validate_configuration(
        self,
    ) -> None:
        """
        Validate MetricsService configuration.
        """

        family_weight_sum = (

            self.config.opportunity_weight
            + self.config.risk_weight
            + self.config.trend_weight
            + self.config.momentum_weight
            + self.config.volume_weight
            + self.config.ranking_weight

        )

        if not math.isclose(
            family_weight_sum,
            1.0,
            rel_tol=1e-9,
        ):
            raise ValueError(
                (
                    "Metric family weights must sum "
                    f"to 1.0 (received "
                    f"{family_weight_sum:.4f})."
                )
            )

        composite_weight_sum = (

            self.config.institutional_weight
            + self.config.alpha_weight
            + self.config.execution_weight
            + self.config.portfolio_weight

        )

        if not math.isclose(
            composite_weight_sum,
            1.0,
            rel_tol=1e-9,
        ):
            raise ValueError(
                (
                    "Composite engine weights must sum "
                    f"to 1.0 (received "
                    f"{composite_weight_sum:.4f})."
                )
            )

    # -------------------------------------------------------------------------
    # Registration
    # -------------------------------------------------------------------------

    def register(
        self,
        calculator,
    ) -> None:
        """
        Register a metric calculation function.

        Each function accepts and returns a DataFrame.

        Example
        -------
        self.register(
            self._calculate_opportunity_metrics
        )
        """

        self._metric_groups.append(
            calculator,
        )

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    def _reset_statistics(
        self,
        rows: int,
    ) -> None:

        self.statistics = MetricStatistics(
            total_rows=rows,
        )

    def _update_success(self) -> None:

        self.statistics.calculated_metrics += 1

    def _update_failure(
        self,
        name: str,
    ) -> None:

        self.statistics.failed_metrics += 1

        self.statistics.warnings.append(
            name,
        )

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def _prepare(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if self.config.copy_dataframe:

            dataframe = dataframe.copy()

        dataframe = _prepare_dataframe(
            dataframe,
        )

        self._reset_statistics(
            len(dataframe),
        )

        return dataframe

    # -------------------------------------------------------------------------
    # Metric Execution
    # -------------------------------------------------------------------------

    def _run_metric_groups(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if not self._metric_groups:

            logger.info(
                "No metric groups registered."
            )

            return dataframe

        for calculator in self._metric_groups:

            try:

                dataframe = calculator(
                    dataframe,
                )

                self._update_success()

                logger.debug(
                    "Completed %s",
                    calculator.__name__,
                )

            except Exception as exc:

                self._update_failure(
                    calculator.__name__,
                )

                logger.exception(
                    "Metric group failed: %s",
                    calculator.__name__,
                )

                logger.debug(
                    exc,
                )

        return dataframe
      
    # -------------------------------------------------------------------------
    # Opportunity Metrics
    # -------------------------------------------------------------------------

    def _calculate_opportunity_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate opportunity related metrics.

        Generated Metrics
        -----------------
        Remaining Upside %
        Entry Distance %
        Target Completion %
        Return / Day
        Risk / Day
        Capital Efficiency
        Opportunity Efficiency
        Confidence Weighted Return
        ATR Adjusted Return
        Stop Cushion
        """

        logger.info(
            "Calculating opportunity metrics."
        )

        df = dataframe

        # -------------------------------------------------------------
        # Remaining Upside %
        # -------------------------------------------------------------

        df["remaining_upside_pct"] = _round(
            _safe_percentage(
                df[ScannerColumns.TARGET]
                - df[ScannerColumns.CMP],
                df[ScannerColumns.CMP],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Entry Distance %
        # -------------------------------------------------------------

        df["entry_distance_pct"] = _round(
            _safe_percentage(
                df[ScannerColumns.CMP]
                - df[ScannerColumns.ENTRY],
                df[ScannerColumns.ENTRY],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Target Completion %
        # -------------------------------------------------------------

        total_move = (
            df[ScannerColumns.TARGET]
            - df[ScannerColumns.ENTRY]
        )

        achieved_move = (
            df[ScannerColumns.CMP]
            - df[ScannerColumns.ENTRY]
        )

        df["target_completion_pct"] = _round(
            _safe_percentage(
                achieved_move,
                total_move,
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Return / Day
        # -------------------------------------------------------------

        df["return_per_day_pct"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.EXPECTED_RETURN_PCT
                ],
                df[
                    ScannerColumns.HOLD_DAYS
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Risk / Day
        # -------------------------------------------------------------

        df["risk_per_day_pct"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.RISK_PCT
                ],
                df[
                    ScannerColumns.HOLD_DAYS
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Capital Efficiency
        # -------------------------------------------------------------

        df["capital_efficiency"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.EXPECTED_RETURN_POINTS
                ],
                df[
                    ScannerColumns.ENTRY
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Opportunity Efficiency
        # -------------------------------------------------------------

        df["opportunity_efficiency"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.EXPECTED_RETURN_PCT
                ],
                df[
                    ScannerColumns.RISK_PCT
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Confidence Weighted Return
        # -------------------------------------------------------------

        df["confidence_weighted_return"] = _round(
            (
                df[
                    ScannerColumns.EXPECTED_RETURN_PCT
                ]
                *
                df[
                    ScannerColumns.CONFIDENCE
                ]
            )
            / 100.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # ATR Adjusted Return
        # -------------------------------------------------------------

        df["atr_adjusted_return"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.EXPECTED_RETURN_PCT
                ],
                df[
                    ScannerColumns.ATR_PCT
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Stop Cushion %
        # -------------------------------------------------------------

        df["stop_cushion_pct"] = _round(
            _safe_percentage(
                df[
                    ScannerColumns.CMP
                ]
                -
                df[
                    ScannerColumns.STOP
                ],
                df[
                    ScannerColumns.CMP
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Normalized Opportunity Score
        # -------------------------------------------------------------

        df[MetricColumns.OPPORTUNITY_SCORE] = _normalize(
            (
                df[
                    "remaining_upside_pct"
                ]
                * 0.30
                +
                df[
                    "opportunity_efficiency"
                ]
                * 0.25
                +
                df[
                    "confidence_weighted_return"
                ]
                * 0.20
                +
                df[
                    "atr_adjusted_return"
                ]
                * 0.15
                +
                df[
                    "capital_efficiency"
                ]
                * 0.10
            )
        )

        logger.info(
            "Calculated %d opportunity metrics.",
            11,
        )

        return df

    # -------------------------------------------------------------------------
    # Risk Metrics
    # -------------------------------------------------------------------------

    def _calculate_risk_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate institutional risk metrics.
        """

        logger.info(
            "Calculating risk metrics."
        )

        df = dataframe

        # -------------------------------------------------------------
        # Downside Exposure %
        # -------------------------------------------------------------

        df["downside_exposure_pct"] = _round(
            _safe_percentage(
                df[ScannerColumns.CMP]
                - df[ScannerColumns.STOP],
                df[ScannerColumns.CMP],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Target / Stop Distance Ratio
        # -------------------------------------------------------------

        target_distance = (
            df[ScannerColumns.TARGET]
            - df[ScannerColumns.CMP]
        )

        stop_distance = (
            df[ScannerColumns.CMP]
            - df[ScannerColumns.STOP]
        )

        df["target_stop_distance_ratio"] = _round(
            _safe_divide(
                target_distance,
                stop_distance,
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # ATR Risk Multiple
        # -------------------------------------------------------------

        df["atr_risk_multiple"] = _round(
            _safe_divide(
                df[ScannerColumns.RISK_PCT],
                df[ScannerColumns.ATR_PCT],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Return / ATR
        # -------------------------------------------------------------

        df["return_to_atr_ratio"] = _round(
            _safe_divide(
                df[ScannerColumns.EXPECTED_RETURN_PCT],
                df[ScannerColumns.ATR_PCT],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Risk Adjusted Return
        # -------------------------------------------------------------

        df["risk_adjusted_return"] = _round(
            _safe_divide(
                df["return_per_day_pct"],
                df["risk_per_day_pct"],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Volatility Efficiency
        # -------------------------------------------------------------

        df["volatility_efficiency"] = _round(
            _safe_divide(
                df[ScannerColumns.EXPECTED_RETURN_PCT],
                (
                    df[ScannerColumns.ATR_PCT]
                    * df[ScannerColumns.RISK_PCT]
                ),
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Stop Loss Buffer
        # -------------------------------------------------------------

        df["stop_loss_buffer"] = _round(
            (
                df[ScannerColumns.ENTRY]
                - df[ScannerColumns.STOP]
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Recovery Factor
        # -------------------------------------------------------------

        df["recovery_factor"] = _round(
            _safe_divide(
                df[ScannerColumns.EXPECTED_RETURN_POINTS],
                df[ScannerColumns.RISK_POINTS],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Risk Quality Score
        # -------------------------------------------------------------

        df[MetricColumns.RISK_SCORE] = _weighted_score(
            {
                "rr": (
                    df[ScannerColumns.RISK_REWARD],
                    0.35,
                ),
                "rar": (
                    df["risk_adjusted_return"],
                    0.25,
                ),
                "recovery": (
                    df["recovery_factor"],
                    0.20,
                ),
                "volatility": (
                    df["volatility_efficiency"],
                    0.20,
                ),
            },
            normalize=True,
        )

        df["risk_quintile"] = _quintile(
            df[MetricColumns.RISK_SCORE],
        )

        df["risk_decile"] = _decile(
            df[MetricColumns.RISK_SCORE],
        )

        logger.info(
            "Calculated risk metrics."
        )

        return df

    # -------------------------------------------------------------------------
    # Trend Metrics
    # -------------------------------------------------------------------------

    def _calculate_trend_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate institutional trend metrics.
        """

        logger.info(
            "Calculating trend metrics."
        )

        df = dataframe

        # -------------------------------------------------------------
        # Trend Alignment
        # -------------------------------------------------------------

        df[MetricColumns.TREND_ALIGNMENT] = (
            df[ScannerColumns.ABOVE_50DMA].astype(int)
            + df[ScannerColumns.ABOVE_200DMA].astype(int)
        )

        # -------------------------------------------------------------
        # Trend Strength
        # -------------------------------------------------------------

        df[MetricColumns.TREND_STRENGTH] = (
            df[MetricColumns.TREND_ALIGNMENT] * 50.0
        )

        # -------------------------------------------------------------
        # Momentum Trend Ratio
        # -------------------------------------------------------------

        df["momentum_trend_ratio"] = _round(
            _safe_divide(
                df[ScannerColumns.ROC],
                df[ScannerColumns.ATR_PCT],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # RSI Trend Score
        # -------------------------------------------------------------

        df["rsi_trend_score"] = (
            100.0
            - (
                (
                    df[ScannerColumns.RSI]
                    - 60.0
                ).abs()
                / 40.0
                * 100.0
            )
        ).clip(
            lower=0.0,
            upper=100.0,
        )

        # -------------------------------------------------------------
        # Breakout Strength
        # -------------------------------------------------------------

        df[MetricColumns.BREAKOUT_STRENGTH] = _round(
            df[MetricColumns.TREND_STRENGTH]
            *
            (
                df[ScannerColumns.VOLUME_RATIO]
                / 2.0
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Trend Conviction
        # -------------------------------------------------------------

        df[MetricColumns.TREND_CONVICTION] = _round(
            (
                df[MetricColumns.TREND_STRENGTH]
                * 0.40
                +
                _normalize(
                    df[ScannerColumns.ROC]
                ) * 0.30
                +
                _normalize(
                    df[ScannerColumns.RSI]
                ) * 0.20
                +
                _normalize(
                    df[ScannerColumns.VOLUME_RATIO]
                ) * 0.10
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Trend Score
        # -------------------------------------------------------------

        df[MetricColumns.TREND_SCORE] = _weighted_score(
            {
                "trend": (
                    df[MetricColumns.TREND_STRENGTH],
                    0.35,
                ),
                "conviction": (
                    df[MetricColumns.TREND_CONVICTION],
                    0.30,
                ),
                "breakout": (
                    df[MetricColumns.BREAKOUT_STRENGTH],
                    0.20,
                ),
                "momentum": (
                    df["momentum_trend_ratio"],
                    0.15,
                ),
            },
            normalize=True,
        )

        df["trend_quintile"] = _quintile(
            df[MetricColumns.TREND_SCORE],
        )

        df["trend_decile"] = _decile(
            df[MetricColumns.TREND_SCORE],
        )

        logger.info(
            "Calculated trend metrics."
        )

        return df

    # -------------------------------------------------------------------------
    # Momentum Metrics
    # -------------------------------------------------------------------------

    def _calculate_momentum_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate institutional momentum metrics.
        """

        logger.info(
            "Calculating momentum metrics.",
        )

        df = dataframe

        # -------------------------------------------------------------
        # ROC Strength
        # -------------------------------------------------------------

        df["roc_strength"] = _normalize(
            df[
                ScannerColumns.ROC
            ],
        )

        # -------------------------------------------------------------
        # RSI Strength
        # -------------------------------------------------------------

        df["rsi_strength"] = _normalize(
            (
                100.0
                -
                (
                    df[
                        ScannerColumns.RSI
                    ]
                    -
                    60.0
                ).abs()
            ),
        )

        # -------------------------------------------------------------
        # Momentum Acceleration
        # -------------------------------------------------------------

        df["momentum_acceleration"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.ROC
                ],
                df[
                    ScannerColumns.ATR_PCT
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Momentum Persistence
        # -------------------------------------------------------------

        df["momentum_persistence"] = _round(
            (
                df[
                    "trend_strength"
                ]
                *
                df[
                    ScannerColumns.VOLUME_RATIO
                ]
            )
            / 100.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Relative Momentum
        # -------------------------------------------------------------

        df["relative_momentum"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.ROC
                ]
                *
                df[
                    ScannerColumns.CONFIDENCE
                ],
                100.0,
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Momentum Efficiency
        # -------------------------------------------------------------

        df["momentum_efficiency"] = _round(
            _safe_divide(
                df[
                    "remaining_upside_pct"
                ],
                df[
                    ScannerColumns.ATR_PCT
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Conviction Momentum
        # -------------------------------------------------------------

        df["conviction_momentum"] = _round(
            (
                df[
                    "relative_momentum"
                ]
                *
                df[
                    ScannerColumns.CONFIDENCE
                ]
            )
            / 100.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Momentum Quality
        # -------------------------------------------------------------

        df[MetricColumns.MOMENTUM_QUALITY] = _round(
            _safe_divide(
                df[
                    "momentum_efficiency"
                ],
                (
                    1.0
                    +
                    df[
                        ScannerColumns.RISK_PCT
                    ]
                ),
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Momentum Score
        # -------------------------------------------------------------

        df[MetricColumns.MOMENTUM_SCORE] = _weighted_score(
            {
                "roc": (
                    df["roc_strength"],
                    0.25,
                ),
                "rsi": (
                    df["rsi_strength"],
                    0.20,
                ),
                "quality": (
                    df[MetricColumns.MOMENTUM_QUALITY],
                    0.20,
                ),
                "acceleration": (
                    df["momentum_acceleration"],
                    0.15,
                ),
                "efficiency": (
                    df["momentum_efficiency"],
                    0.10,
                ),
                "persistence": (
                    df["momentum_persistence"],
                    0.10,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Institutional Classification
        # -------------------------------------------------------------

        df["momentum_band"] = _score_band(
            df[
                "momentum_score"
            ],
        )

        df["momentum_quintile"] = _quintile(
            df[
                "momentum_score"
            ],
        )

        df["momentum_decile"] = _decile(
            df[
                "momentum_score"
            ],
        )

        logger.info(
            "Calculated momentum metrics.",
        )

        return df

    # -------------------------------------------------------------------------
    # Volume & Liquidity Metrics
    # -------------------------------------------------------------------------

    def _calculate_volume_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Institutional volume and liquidity metrics.
        """

        logger.info(
            "Calculating volume metrics.",
        )

        df = dataframe

        # -------------------------------------------------------------
        # Volume Strength
        # -------------------------------------------------------------

        df["volume_strength"] = _normalize(
            df[
                ScannerColumns.VOLUME_RATIO
            ],
        )

        # -------------------------------------------------------------
        # Liquidity Score
        # -------------------------------------------------------------

        df[MetricColumns.LIQUIDITY_SCORE] = _normalize(
            np.log1p(
                df[
                    ScannerColumns.VOLUME
                ]
            ),
        )

        # -------------------------------------------------------------
        # Participation Score
        # -------------------------------------------------------------

        df["participation_score"] = _round(
            df[
                "volume_strength"
            ]
            *
            (
                df[
                    ScannerColumns.CONFIDENCE
                ]
                / 100.0
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Volume Conviction
        # -------------------------------------------------------------

        df["volume_conviction"] = _round(
            df[
                ScannerColumns.VOLUME_RATIO
            ]
            *
            (
                df[
                    ScannerColumns.CONFIDENCE
                ]
                / 100.0
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Volume Efficiency
        # -------------------------------------------------------------

        df["volume_efficiency"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.EXPECTED_RETURN_PCT
                ],
                df[
                    ScannerColumns.VOLUME_RATIO
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Liquidity Efficiency
        # -------------------------------------------------------------

        df["liquidity_efficiency"] = _round(
            _safe_divide(
                df[
                    "opportunity_score"
                ],
                (
                    1.0
                    +
                    df[
                        ScannerColumns.ATR_PCT
                    ]
                ),
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Institutional Participation
        # -------------------------------------------------------------

        df["institutional_participation"] = _round(
            (
                df[
                    "liquidity_score"
                ]
                * 0.40
                +
                df[
                    "volume_strength"
                ]
                * 0.30
                +
                _normalize(
                    df[
                        ScannerColumns.CONFIDENCE
                    ]
                )
                * 0.30
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Accumulation Score
        # -------------------------------------------------------------

        df["accumulation_score"] = _round(
            (
                df[
                    ScannerColumns.VOLUME_RATIO
                ]
                *
                df[
                    ScannerColumns.ROC
                ]
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Distribution Risk
        # -------------------------------------------------------------

        df["distribution_risk"] = _round(
            _safe_divide(
                df[
                    ScannerColumns.ATR_PCT
                ],
                (
                    1.0
                    +
                    df[
                        ScannerColumns.VOLUME_RATIO
                    ]
                ),
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Turnover Quality
        # -------------------------------------------------------------

        df["turnover_quality"] = _round(
            (
                df[
                    "volume_strength"
                ]
                *
                df[
                    "trend_score"
                ]
            )
            / 100.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Volume Score
        # -------------------------------------------------------------

        df[MetricColumns.VOLUME_SCORE] = _weighted_score(
            {
                "liquidity": (
                    df[MetricColumns.LIQUIDITY_SCORE],
                    0.25,
                ),
                "participation": (
                    df["participation_score"],
                    0.20,
                ),
                "conviction": (
                    df["volume_conviction"],
                    0.20,
                ),
                "efficiency": (
                    df["volume_efficiency"],
                    0.15,
                ),
                "institutional": (
                    df["institutional_participation"],
                    0.10,
                ),
                "turnover": (
                    df["turnover_quality"],
                    0.10,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Institutional Classification
        # -------------------------------------------------------------

        df["volume_band"] = _score_band(
            df[
                "volume_score"
            ],
        )

        df["volume_quintile"] = _quintile(
            df[
                "volume_score"
            ],
        )

        df["volume_decile"] = _decile(
            df[
                "volume_score"
            ],
        )

        logger.info(
            "Calculated volume metrics.",
        )

        return df

    # -------------------------------------------------------------------------
    # Quality Metrics
    # -------------------------------------------------------------------------

    def _calculate_quality_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Institutional quality metrics.
        """

        logger.info(
            "Calculating quality metrics.",
        )

        df = dataframe

        # -------------------------------------------------------------
        # Confidence Quality
        # -------------------------------------------------------------

        df[MetricColumns.CONFIDENCE_QUALITY] = _normalize(
            df[
                ScannerColumns.CONFIDENCE
            ],
        )

        # -------------------------------------------------------------
        # Reward Quality
        # -------------------------------------------------------------

        df["reward_quality"] = _normalize(
            df[
                ScannerColumns.EXPECTED_RETURN_PCT
            ],
        )

        # -------------------------------------------------------------
        # Risk Quality
        # -------------------------------------------------------------

        df[MetricColumns.RISK_QUALITY] = _normalize(
            df[
                ScannerColumns.RISK_REWARD
            ],
        )

        # -------------------------------------------------------------
        # Trend Quality
        # -------------------------------------------------------------

        df[MetricColumns.TREND_QUALITY] = _round(
            (
                df[MetricColumns.TREND_SCORE]
                +
                df[MetricColumns.MOMENTUM_SCORE]
            )
            / 2.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Liquidity Quality
        # -------------------------------------------------------------

        df[MetricColumns.LIQUIDITY_QUALITY] = _round(
            (
                df[MetricColumns.VOLUME_SCORE]
                +
                df[MetricColumns.LIQUIDITY_SCORE]
            )
            / 2.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Stability Quality
        # -------------------------------------------------------------

        df[MetricColumns.STABILITY_QUALITY] = _round(
            _safe_divide(
                df[MetricColumns.TREND_SCORE],
                (
                    1.0
                    +
                    df[
                        ScannerColumns.ATR_PCT
                    ]
                ),
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Consistency Quality
        # -------------------------------------------------------------

        df[MetricColumns.CONSISTENCY_QUALITY] = _round(
            (
                df[MetricColumns.CONFIDENCE_QUALITY]
                * 0.50
                +
                df[MetricColumns.TREND_SCORE]
                * 0.30
                +
                df[MetricColumns.VOLUME_SCORE]
                * 0.20
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Opportunity Quality
        # -------------------------------------------------------------

        df["opportunity_quality"] = _round(
            (
                df[MetricColumns.OPPORTUNITY_SCORE]
                +
                df[MetricColumns.RISK_SCORE]
            )
            / 2.0,
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Institutional Quality Score
        # -------------------------------------------------------------

        df[MetricColumns.QUALITY_SCORE] = _weighted_score(
            {
                "confidence": (
                    df[MetricColumns.CONFIDENCE_QUALITY],
                    0.20,
                ),
                "reward": (
                    df["reward_quality"],
                    0.15,
                ),
                "risk": (
                    df[MetricColumns.RISK_QUALITY],
                    0.20,
                ),
                "trend": (
                    df[MetricColumns.TREND_QUALITY],
                    0.15,
                ),
                "liquidity": (
                    df[MetricColumns.LIQUIDITY_QUALITY],
                    0.10,
                ),
                "stability": (
                    df[MetricColumns.STABILITY_QUALITY],
                    0.10,
                ),
                "consistency": (
                    df[MetricColumns.CONSISTENCY_QUALITY],
                    0.05,
                ),
                "opportunity": (
                    df["opportunity_quality"],
                    0.05,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Institutional Classification
        # -------------------------------------------------------------

        df["quality_band"] = _score_band(
            df[MetricColumns.QUALITY_SCORE],
        )

        df["quality_quintile"] = _quintile(
            df[MetricColumns.QUALITY_SCORE],
        )

        df["quality_decile"] = _decile(
            df[MetricColumns.QUALITY_SCORE],
        )

        logger.info(
            "Calculated quality metrics.",
        )

        return df

    # -------------------------------------------------------------------------
    # Composite Institutional Metrics
    # -------------------------------------------------------------------------

    def _calculate_composite_metrics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate institutional composite metrics.

        This engine combines the individual metric families
        into portfolio-level institutional scores.

        Generated Metrics
        -----------------
        Institutional Score
        Alpha Score
        Execution Score
        Portfolio Fit Score
        Composite Score
        Institutional Ranking
        Recommendation Metrics
        """

        logger.info(
            "Calculating composite institutional metrics.",
        )

        df = dataframe

        # -------------------------------------------------------------
        # Institutional Score
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_SCORE
        ] = _weighted_score(
            {
                "opportunity": (
                    df[
                        MetricColumns.OPPORTUNITY_SCORE
                    ],
                    self.config.opportunity_weight,
                ),
                "risk": (
                    df[
                        MetricColumns.RISK_SCORE
                    ],
                    self.config.risk_weight,
                ),
                "trend": (
                    df[
                        MetricColumns.TREND_SCORE
                    ],
                    self.config.trend_weight,
                ),
                "momentum": (
                    df[
                        MetricColumns.MOMENTUM_SCORE
                    ],
                    self.config.momentum_weight,
                ),
                "volume": (
                    df[
                        MetricColumns.VOLUME_SCORE
                    ],
                    self.config.volume_weight,
                ),
                "quality": (
                    df[
                        MetricColumns.QUALITY_SCORE
                    ],
                    self.config.ranking_weight,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Alpha Score
        # -------------------------------------------------------------

        df[
            MetricColumns.ALPHA_SCORE
        ] = _weighted_score(
            {
                "opportunity": (
                    df[
                        MetricColumns.OPPORTUNITY_SCORE
                    ],
                    0.45,
                ),
                "trend": (
                    df[
                        MetricColumns.TREND_SCORE
                    ],
                    0.30,
                ),
                "momentum": (
                    df[
                        MetricColumns.MOMENTUM_SCORE
                    ],
                    0.25,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Execution Score
        # -------------------------------------------------------------

        df[
            MetricColumns.EXECUTION_SCORE
        ] = _weighted_score(
            {
                "volume": (
                    df[
                        MetricColumns.VOLUME_SCORE
                    ],
                    0.40,
                ),
                "risk": (
                    df[
                        MetricColumns.RISK_SCORE
                    ],
                    0.30,
                ),
                "liquidity": (
                    df[
                        MetricColumns.LIQUIDITY_QUALITY
                    ],
                    0.15,
                ),
                "confidence": (
                    df[
                        MetricColumns.CONFIDENCE_QUALITY
                    ],
                    0.15,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Portfolio Fit Score
        # -------------------------------------------------------------

        df[
            MetricColumns.PORTFOLIO_FIT_SCORE
        ] = _weighted_score(
            {
                "quality": (
                    df[
                        MetricColumns.QUALITY_SCORE
                    ],
                    0.40,
                ),
                "risk": (
                    df[
                        MetricColumns.RISK_SCORE
                    ],
                    0.30,
                ),
                "opportunity": (
                    df[
                        MetricColumns.OPPORTUNITY_SCORE
                    ],
                    0.30,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Composite Score
        # -------------------------------------------------------------

        df[
            MetricColumns.COMPOSITE_SCORE
        ] = _weighted_score(
            {
                "institutional": (
                    df[
                        MetricColumns.INSTITUTIONAL_SCORE
                    ],
                    self.config.institutional_weight,
                ),
                "alpha": (
                    df[
                        MetricColumns.ALPHA_SCORE
                    ],
                    self.config.alpha_weight,
                ),
                "execution": (
                    df[
                        MetricColumns.EXECUTION_SCORE
                    ],
                    self.config.execution_weight,
                ),
                "portfolio": (
                    df[
                        MetricColumns.PORTFOLIO_FIT_SCORE
                    ],
                    self.config.portfolio_weight,
                ),
            },
            normalize=True,
        )

        # -------------------------------------------------------------
        # Institutional Rank
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_RANK
        ] = (
            df[
                MetricColumns.COMPOSITE_SCORE
            ]
            .rank(
                ascending=False,
                method="dense",
            )
            .astype("Int64")
        )

        # -------------------------------------------------------------
        # Institutional Percentile
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_PERCENTILE
        ] = _round(
            _percentile_rank(
                df[
                    MetricColumns.COMPOSITE_SCORE
                ],
            ),
            self.config.rounding_digits,
        )

        # -------------------------------------------------------------
        # Institutional Quintile
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_QUINTILE
        ] = _quintile(
            df[
                MetricColumns.COMPOSITE_SCORE
            ],
        )

        # -------------------------------------------------------------
        # Institutional Decile
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_DECILE
        ] = _decile(
            df[
                MetricColumns.COMPOSITE_SCORE
            ],
        )

        # -------------------------------------------------------------
        # Institutional Grade
        # -------------------------------------------------------------

        df[
            MetricColumns.INSTITUTIONAL_GRADE
        ] = pd.cut(
            df[
                MetricColumns.COMPOSITE_SCORE
            ],
            bins=[
                -np.inf,
                20.0,
                40.0,
                60.0,
                80.0,
                np.inf,
            ],
            labels=[
                "E",
                "D",
                "C",
                "B",
                "A",
            ],
        )

        # -------------------------------------------------------------
        # Recommendation Score
        # -------------------------------------------------------------

        df[
            MetricColumns.RECOMMENDATION_SCORE
        ] = _round(
            (
                df[
                    MetricColumns.COMPOSITE_SCORE
                ]
                * self.config.recommendation_composite_weight

                +

                df[
                    MetricColumns.QUALITY_SCORE
                ]
                * self.config.recommendation_quality_weight

                +

                df[
                    MetricColumns.OPPORTUNITY_SCORE
                ]
                * self.config.recommendation_opportunity_weight

                +

                df[
                    MetricColumns.RISK_SCORE
                ]
                * self.config.recommendation_risk_weight
            ),
            self.config.rounding_digits,
        )
      
        # -------------------------------------------------------------
        # Recommendation Band
        # -------------------------------------------------------------

        df[
            MetricColumns.RECOMMENDATION_BAND
        ] = _score_band(
            df[
                MetricColumns.RECOMMENDATION_SCORE
            ],
        )

        # -------------------------------------------------------------
        # Institutional Recommendation
        # -------------------------------------------------------------

        recommendation_score = df[
            MetricColumns.RECOMMENDATION_SCORE
        ]

        strong_buy = recommendation_score.quantile(
            0.95,
        )

        buy = recommendation_score.quantile(
            0.80,
        )

        watch = recommendation_score.quantile(
            0.60,
        )

        hold = recommendation_score.quantile(
            0.40,
        )

        df[
            ScannerColumns.RECOMMENDATION
        ] = np.select(

            [
                recommendation_score >= strong_buy,
                recommendation_score >= buy,
                recommendation_score >= watch,
                recommendation_score >= hold,
            ],

            [
                "STRONG BUY",
                "BUY",
                "WATCH",
                "HOLD",
            ],

            default="AVOID",

        )
        
        # -------------------------------------------------------------
        # Top Decile Flag
        # -------------------------------------------------------------

        df[
            MetricColumns.TOP_DECILE
        ] = (
            df[
                MetricColumns.INSTITUTIONAL_DECILE
            ]
            == 10
        )

        # -------------------------------------------------------------
        # Top Quintile Flag
        # -------------------------------------------------------------

        df[
            MetricColumns.TOP_QUINTILE
        ] = (
            df[
                MetricColumns.INSTITUTIONAL_QUINTILE
            ]
            == 5
        )

        # -------------------------------------------------------------
        # Top 10 Percent
        # -------------------------------------------------------------

        df[
            MetricColumns.TOP_10_PERCENT
        ] = _top_percent(
            df[
                MetricColumns.COMPOSITE_SCORE
            ],
            percent=10.0,
        )

        # -------------------------------------------------------------
        # Bottom 10 Percent
        # -------------------------------------------------------------

        df[
            MetricColumns.BOTTOM_10_PERCENT
        ] = _bottom_percent(
            df[
                MetricColumns.COMPOSITE_SCORE
            ],
            percent=10.0,
        )

        # -------------------------------------------------------------
        # Summary Statistics
        # -------------------------------------------------------------

        logger.info(
            (
                "Composite metrics calculated for %d "
                "securities."
            ),
            len(df),
        )

        logger.debug(
            (
                "Average Composite Score: %.2f | "
                "Maximum: %.2f | "
                "Minimum: %.2f"
            ),
            df[
                MetricColumns.COMPOSITE_SCORE
            ].mean(),
            df[
                MetricColumns.COMPOSITE_SCORE
            ].max(),
            df[
                MetricColumns.COMPOSITE_SCORE
            ].min(),
        )

        logger.info(
            "Composite institutional metrics completed.",
        )

        return df
      
  
    # -------------------------------------------------------------------------
    # Finalization
    # -------------------------------------------------------------------------

    def _finalize(
        self,
        dataframe: pd.DataFrame,
    ) -> MetricsResult:

        self.statistics.skipped_metrics = max(
            0,
            len(self._metric_groups)
            - self.statistics.calculated_metrics
            - self.statistics.failed_metrics,
        )

        return MetricsResult(
            dataframe=dataframe,
            statistics=self.statistics,
            metadata={
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
                "metric_groups": len(
                    self._metric_groups,
                ),
            },
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def calculate(
        self,
        dataframe: pd.DataFrame,
    ) -> MetricsResult:
        """
        Calculate all registered metrics.

        Parameters
        ----------
        dataframe
            Scanner output.

        Returns
        -------
        MetricsResult
        """

        logger.info(
            "Starting metric calculations."
        )

        dataframe = self._prepare(
            dataframe,
        )

        dataframe = self._run_metric_groups(
            dataframe,
        )

        logger.info(
            "Metric calculation completed."
        )

        return self._finalize(
            dataframe,
        )
