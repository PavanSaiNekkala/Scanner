"""
validation.py
=============

Institutional Validation Framework.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import BacktestConfig
from .orders import Order
from .exceptions import (
    ConfigurationError,
    DataError,
    InvalidOrderError,
    PortfolioConstraintError,
)


# ==========================================================
# Validation Result
# ==========================================================


@dataclass(slots=True)
class ValidationResult:
    """
    Validation result.
    """

    passed: bool

    message: str = ""

    details: dict | None = None


# ==========================================================
# Validator
# ==========================================================


class Validator:
    """
    Institutional validation engine.
    """

    def __init__(
        self,
        config: BacktestConfig,
    ) -> None:

        self.config = config


    def validate_config(
        self,
    ) -> ValidationResult:
        """
        Validate configuration.
        """

        if self.config.initial_capital <= 0:

            raise ConfigurationError(
                "Initial capital must be positive."
            )

        if self.config.leverage <= 0:

            raise ConfigurationError(
                "Leverage must be positive."
            )

        if not (
            0
            < self.config.max_position_weight
            <= 1
        ):

            raise ConfigurationError(
                "Invalid max_position_weight."
            )

        if (
            self.config.max_positions
            <= 0
        ):

            raise ConfigurationError(
                "max_positions must be positive."
            )

        return ValidationResult(
            True,
            "Configuration validated.",
        )


    def validate_order(
        self,
        order: Order,
    ) -> ValidationResult:
        """
        Validate an order.
        """

        if not order.symbol:

            raise InvalidOrderError(
                "Missing symbol."
            )

        if order.quantity <= 0:

            raise InvalidOrderError(
                "Quantity must be positive."
            )

        if (
            order.limit_price
            is not None
            and order.limit_price <= 0
        ):

            raise InvalidOrderError(
                "Invalid limit price."
            )

        if (
            order.stop_price
            is not None
            and order.stop_price <= 0
        ):

            raise InvalidOrderError(
                "Invalid stop price."
            )

        return ValidationResult(
            True,
            "Order validated.",
        )


    def validate_market_data(
        self,
        data: pd.DataFrame,
    ) -> ValidationResult:
        """
        Validate OHLCV data.
        """

        required = {
            "Open",
            "High",
            "Low",
            "Close",
        }

        missing = required - set(
            data.columns
        )

        if missing:

            raise DataError(
                f"Missing columns: {missing}"
            )

        if data.empty:

            raise DataError(
                "Empty DataFrame."
            )

        if (
            data["High"]
            < data["Low"]
        ).any():

            raise DataError(
                "High < Low detected."
            )

        return ValidationResult(
            True,
            "Market data validated.",
        )


    def validate_trade(
        self,
        symbol: str,
        quantity: float,
        price: float,
    ) -> ValidationResult:
        """
        Validate a trade.
        """

        if not symbol:
            raise InvalidOrderError(
                "Trade symbol cannot be empty."
            )

        if quantity <= 0:
            raise InvalidOrderError(
                "Trade quantity must be positive."
            )

        if price <= 0:
            raise InvalidOrderError(
                "Trade price must be positive."
            )

        return ValidationResult(
            True,
            "Trade validated.",
        )

    def validate_position(
        self,
        quantity: float,
        market_value: float,
    ) -> ValidationResult:
        """
        Validate a position.
        """

        if market_value < 0:
            raise PortfolioConstraintError(
                "Negative market value."
            )

        if quantity == 0:
            return ValidationResult(
                True,
                "Flat position.",
            )

        return ValidationResult(
            True,
            "Position validated.",
        )

    def validate_portfolio(
        self,
        weights: pd.Series,
    ) -> ValidationResult:
        """
        Validate portfolio weights.
        """

        if weights.empty:
            raise PortfolioConstraintError(
                "Portfolio is empty."
            )

        if (weights < 0).any():
            raise PortfolioConstraintError(
                "Negative portfolio weights detected."
            )

        total = weights.sum()

        if total > 1.001:
            raise PortfolioConstraintError(
                f"Portfolio weights exceed 100% ({total:.2%})."
            )

        if (
            weights.max()
            > self.config.max_position_weight
        ):
            raise PortfolioConstraintError(
                "Maximum position weight exceeded."
            )

        return ValidationResult(
            True,
            "Portfolio validated.",
        )

    def validate_benchmark(
        self,
        benchmark: pd.Series,
    ) -> ValidationResult:
        """
        Validate benchmark returns.
        """

        if benchmark.empty:
            raise DataError(
                "Benchmark data is empty."
            )

        if benchmark.isna().all():
            raise DataError(
                "Benchmark contains only missing values."
            )

        return ValidationResult(
            True,
            "Benchmark validated.",
        )

    def validate_returns(
        self,
        returns: pd.Series,
    ) -> ValidationResult:
        """
        Validate return series.
        """

        if returns.empty:
            raise DataError(
                "Return series is empty."
            )

        if returns.isna().all():
            raise DataError(
                "Return series contains only NaN values."
            )

        if (
            returns.abs() > 10
        ).any():
            raise DataError(
                "Unrealistic return values detected."
            )

        return ValidationResult(
            True,
            "Returns validated.",
        )

    def validate_weights(
        self,
        weights: pd.Series,
    ) -> ValidationResult:
        """
        Validate allocation weights.
        """

        if weights.empty:
            raise PortfolioConstraintError(
                "Weight series is empty."
            )

        if (weights < 0).any():
            raise PortfolioConstraintError(
                "Negative weights detected."
            )

        if (
            weights
            > self.config.max_position_weight
        ).any():
            raise PortfolioConstraintError(
                "Position weight exceeds configured maximum."
            )

        return ValidationResult(
            True,
            "Weights validated.",
        )

    def validate_prices(
        self,
        prices: pd.Series,
    ) -> ValidationResult:
        """
        Validate price series.
        """

        if prices.empty:
            raise DataError(
                "Price series is empty."
            )

        if prices.isna().all():
            raise DataError(
                "Price series contains only NaN values."
            )

        if (prices <= 0).any():
            raise DataError(
                "Prices must be positive."
            )

        return ValidationResult(
            True,
            "Prices validated.",
        )

    def validate_dates(
        self,
        data: pd.DataFrame,
    ) -> ValidationResult:
        """
        Validate datetime index.
        """

        if not isinstance(
            data.index,
            pd.DatetimeIndex,
        ):
            raise DataError(
                "Index must be DatetimeIndex."
            )

        if not data.index.is_monotonic_increasing:
            raise DataError(
                "Datetime index must be sorted."
            )

        if data.index.has_duplicates:
            raise DataError(
                "Duplicate timestamps detected."
            )

        return ValidationResult(
            True,
            "Dates validated.",
        )

    def validate_symbols(
        self,
        symbols: list[str],
    ) -> ValidationResult:
        """
        Validate security symbols.
        """

        if not symbols:
            raise DataError(
                "No symbols provided."
            )

        duplicates = {
            symbol
            for symbol in symbols
            if symbols.count(symbol) > 1
        }

        if duplicates:
            raise DataError(
                f"Duplicate symbols: {sorted(duplicates)}"
            )

        invalid = [
            symbol
            for symbol in symbols
            if not symbol
            or not isinstance(
                symbol,
                str,
            )
        ]

        if invalid:
            raise DataError(
                "Invalid symbols detected."
            )

        return ValidationResult(
            True,
            "Symbols validated.",
        )

    def validate_dataframe(
        self,
        data: pd.DataFrame,
        required_columns: list[str] | None = None,
    ) -> ValidationResult:
        """
        Generic DataFrame validation.
        """

        if data.empty:
            raise DataError(
                "DataFrame is empty."
            )

        if required_columns:

            missing = [
                column
                for column
                in required_columns
                if column not in data.columns
            ]

            if missing:
                raise DataError(
                    f"Missing columns: {missing}"
                )

        return ValidationResult(
            True,
            "DataFrame validated.",
        )

    def validate(
        self,
        data: pd.DataFrame,
        order: Order | None = None,
    ) -> ValidationResult:
        """
        Perform complete validation.
        """

        self.validate_config()

        self.validate_market_data(
            data,
        )

        self.validate_dates(
            data,
        )

        if order is not None:
            self.validate_order(
                order,
            )

        return ValidationResult(
            True,
            "Validation completed successfully.",
        )

    def reset(
        self,
    ) -> None:
        """
        Reset validator state.
        """

        # Stateless validator.
        return