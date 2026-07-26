"""
config.py
=========

Institutional Backtest Configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# ==========================================================
# Backtest Configuration
# ==========================================================


@dataclass(slots=True)
class BacktestConfig:
    """
    Configuration for the institutional backtest engine.
    """

    # ======================================================
    # Paths
    # ======================================================

    output_directory: Path = Path("outputs/backtest")

    benchmark_symbol: str = "NIFTY 50"

    report_name: str = "institutional_backtest"

    # ======================================================
    # Dates
    # ======================================================

    start_date: str | None = None

    end_date: str | None = None

    rebalance_frequency: str = "Monthly"

    # Daily | Weekly | Monthly | Quarterly

    # ======================================================
    # Capital
    # ======================================================

    initial_capital: float = 10_000_000.0

    currency: str = "INR"

    allow_fractional_shares: bool = False

    leverage: float = 1.0

    margin_requirement: float = 1.0

    # ======================================================
    # Position Limits
    # ======================================================

    max_positions: int = 50

    max_position_weight: float = 0.05

    min_position_weight: float = 0.005

    max_sector_weight: float = 0.30

    # ======================================================
    # Costs
    # ======================================================

    brokerage: float = 0.0003

    exchange_fee: float = 0.0000325

    taxes: float = 0.0005

    slippage: float = 0.0005

    market_impact: float = 0.0002

    # ======================================================
    # Execution
    # ======================================================

    execution_model: str = "VWAP"

    participation_rate: float = 0.10

    # ======================================================
    # Risk
    # ======================================================

    annualization_factor: int = 252

    risk_free_rate: float = 0.06

    confidence_level: float = 0.95

    max_drawdown_limit: float = 0.20

    stop_loss: float | None = None

    take_profit: float | None = None

    # ======================================================
    # Benchmark
    # ======================================================

    compare_with_benchmark: bool = True

    benchmark_rebalance: bool = False

    # ======================================================
    # Reports
    # ======================================================

    export_excel: bool = True

    export_csv: bool = True

    export_json: bool = True

    export_html: bool = True

    save_trade_log: bool = True

    save_equity_curve: bool = True

    # ======================================================
    # Logging
    # ======================================================

    verbose: bool = True

    random_seed: int = 42

    metadata: dict = field(
        default_factory=dict,
    )

    def copy(
        self,
    ) -> "BacktestConfig":
        """
        Return a copy of the configuration.
        """

        return BacktestConfig(
            **self.to_dict(),
        )

    def update(
        self,
        **kwargs,
    ) -> None:
        """
        Update configuration values.
        """

        valid_fields = {
            field
            for field
            in self.__dataclass_fields__
        }

        for key, value in kwargs.items():

            if key not in valid_fields:

                raise AttributeError(
                    f"Unknown configuration field: {key}"
                )

            setattr(
                self,
                key,
                value,
            )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Convert configuration to a dictionary.
        """

        return {
            field: getattr(
                self,
                field,
            )
            for field
            in self.__dataclass_fields__
        }

    @classmethod
    def from_dict(
        cls,
        config: dict[str, object],
    ) -> "BacktestConfig":
        """
        Create configuration from a dictionary.
        """

        return cls(
            **config,
        )

    def validate(
        self,
    ) -> None:
        """
        Validate configuration values.
        """

        if self.initial_capital <= 0:
            raise ValueError(
                "initial_capital must be positive."
            )

        if self.leverage <= 0:
            raise ValueError(
                "leverage must be positive."
            )

        if not (
            0.0
            < self.max_position_weight
            <= 1.0
        ):
            raise ValueError(
                "max_position_weight must be in (0, 1]."
            )

        if not (
            0.0
            <= self.min_position_weight
            <= self.max_position_weight
        ):
            raise ValueError(
                "min_position_weight must be less than or equal to max_position_weight."
            )

        if self.max_positions <= 0:
            raise ValueError(
                "max_positions must be positive."
            )

        if self.annualization_factor <= 0:
            raise ValueError(
                "annualization_factor must be positive."
            )

        if not (
            0.0
            < self.confidence_level
            < 1.0
        ):
            raise ValueError(
                "confidence_level must be between 0 and 1."
            )

        if not (
            0.0
            <= self.participation_rate
            <= 1.0
        ):
            raise ValueError(
                "participation_rate must be between 0 and 1."
            )

        if not (
            0.0
            <= self.max_sector_weight
            <= 1.0
        ):
            raise ValueError(
                "max_sector_weight must be between 0 and 1."
            )
        

DEFAULT_BACKTEST_CONFIG = BacktestConfig()


__all__ = [
    "BacktestConfig",
    "DEFAULT_BACKTEST_CONFIG",
]