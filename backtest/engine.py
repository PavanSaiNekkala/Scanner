"""
engine.py
=========

Institutional Backtest Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import logging
import numpy as np
import pandas as pd

from .config import BacktestConfig

logger = logging.getLogger(__name__)


# ==========================================================
# Statistics
# ==========================================================


@dataclass(slots=True)
class BacktestStatistics:
    """
    Institutional backtest statistics.
    """

    total_return: float = 0.0

    annual_return: float = 0.0

    annual_volatility: float = 0.0

    sharpe_ratio: float = 0.0

    sortino_ratio: float = 0.0

    calmar_ratio: float = 0.0

    information_ratio: float = 0.0

    beta: float = 0.0

    alpha: float = 0.0

    max_drawdown: float = 0.0

    value_at_risk: float = 0.0

    expected_shortfall: float = 0.0

    turnover: float = 0.0

    total_trades: int = 0

    winning_trades: int = 0

    losing_trades: int = 0

    win_rate: float = 0.0

    average_win: float = 0.0

    average_loss: float = 0.0

    profit_factor: float = 0.0

    expectancy: float = 0.0

    exposure: float = 0.0

    average_holding_period: float = 0.0

    execution_cost: float = 0.0

    slippage_cost: float = 0.0


# ==========================================================
# Result
# ==========================================================


@dataclass(slots=True)
class BacktestResult:
    """
    Institutional backtest output.
    """

    equity_curve: pd.DataFrame

    portfolio_history: pd.DataFrame

    trades: pd.DataFrame

    positions: pd.DataFrame

    orders: pd.DataFrame

    benchmark: pd.DataFrame

    drawdowns: pd.DataFrame

    monthly_returns: pd.DataFrame

    yearly_returns: pd.DataFrame

    attribution: pd.DataFrame

    statistics: BacktestStatistics

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    generated_at: datetime = field(
        default_factory=datetime.now,
    )


# ==========================================================
# Backtest Engine
# ==========================================================


class BacktestEngine:
    """
    Institutional Portfolio Backtesting Engine.

    Pipeline

    Universe
        ↓
    Signals
        ↓
    Portfolio Construction
        ↓
    Risk Checks
        ↓
    Execution Simulation
        ↓
    Portfolio Accounting
        ↓
    Performance Analytics
        ↓
    Reports
    """

    def __init__(
        self,
        config: BacktestConfig | None = None,
    ) -> None:

        self.config = config or BacktestConfig()

        logger.info(
            "Backtest Engine initialized."
        )


    def run(
        self,
        market_data: pd.DataFrame,
        signals: pd.DataFrame,
    ) -> BacktestResult:
        """
        Execute a complete institutional backtest.

        Pipeline
        --------
        1. Validate inputs
        2. Simulate portfolio
        3. Compute statistics
        4. Build result
        """

        logger.info(
            "Starting institutional backtest."
        )

        start_time = datetime.now()

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        self._validate_inputs(
            market_data,
            signals,
        )

        # -----------------------------------------------------
        # Simulation
        # -----------------------------------------------------

        simulation = self._simulate(
            market_data,
            signals,
        )

        # -----------------------------------------------------
        # Performance Statistics
        # -----------------------------------------------------

        statistics = (
            self._performance_statistics(
                simulation["equity_curve"],
                simulation["trades"],
            )
        )

        # -----------------------------------------------------
        # Build Result
        # -----------------------------------------------------

        result = self._build_result(
            simulation,
            statistics,
        )

        # -----------------------------------------------------
        # Metadata
        # -----------------------------------------------------

        result.metadata.update(

            {

                "started_at": start_time,

                "completed_at": datetime.now(),

                "duration_seconds": (
                    datetime.now()
                    - start_time
                ).total_seconds(),

                "initial_capital":
                    self.config.initial_capital,

                "benchmark":
                    self.config.benchmark_symbol,

                "rebalance_frequency":
                    self.config.rebalance_frequency,

                "execution_model":
                    self.config.execution_model,

            }

        )

        logger.info(

            "Backtest completed in %.2f seconds.",

            result.metadata[
                "duration_seconds"
            ],

        )

        return result
    


    def _validate_inputs(
        self,
        market_data: pd.DataFrame,
        signals: pd.DataFrame,
    ) -> None:
        """
        Validate market data, signals, and configuration.
        """

        logger.info(
            "Validating backtest inputs."
        )

        # =====================================================
        # Empty Data
        # =====================================================

        if market_data.empty:
            raise ValueError(
                "Market data is empty."
            )

        if signals.empty:
            raise ValueError(
                "Signals are empty."
            )

        # =====================================================
        # Required Columns
        # =====================================================

        market_required = {

            "date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",

        }

        signal_required = {

            "date",
            "symbol",
            "signal",

        }

        missing_market = (
            market_required
            - set(market_data.columns.str.lower())
        )

        if missing_market:

            raise ValueError(

                "Missing market columns: "
                f"{sorted(missing_market)}"

            )

        missing_signal = (
            signal_required
            - set(signals.columns.str.lower())
        )

        if missing_signal:

            raise ValueError(

                "Missing signal columns: "
                f"{sorted(missing_signal)}"

            )

        # =====================================================
        # Normalize Column Names
        # =====================================================

        market_data.columns = (
            market_data.columns.str.lower()
        )

        signals.columns = (
            signals.columns.str.lower()
        )

        # =====================================================
        # Date Conversion
        # =====================================================

        market_data["date"] = pd.to_datetime(
            market_data["date"],
        )

        signals["date"] = pd.to_datetime(
            signals["date"],
        )

        # =====================================================
        # Missing Values
        # =====================================================

        if market_data.isna().any().any():

            raise ValueError(
                "Market data contains missing values."
            )

        if signals.isna().any().any():

            raise ValueError(
                "Signals contain missing values."
            )

        # =====================================================
        # Duplicate Rows
        # =====================================================

        duplicates = market_data.duplicated(
            subset=[
                "date",
                "symbol",
            ]
        )

        if duplicates.any():

            raise ValueError(

                f"Market data contains "
                f"{duplicates.sum()} duplicates."

            )

        duplicates = signals.duplicated(
            subset=[
                "date",
                "symbol",
            ]
        )

        if duplicates.any():

            raise ValueError(

                f"Signals contain "
                f"{duplicates.sum()} duplicates."

            )

        # =====================================================
        # Numeric Validation
        # =====================================================

        price_columns = [

            "open",
            "high",
            "low",
            "close",

        ]

        for column in price_columns:

            if (
                market_data[column] <= 0
            ).any():

                raise ValueError(

                    f"{column} contains "
                    "non-positive prices."

                )

        if (
            market_data["volume"] < 0
        ).any():

            raise ValueError(
                "Negative volume detected."
            )

        # =====================================================
        # Date Order
        # =====================================================

        if not market_data[
            "date"
        ].is_monotonic_increasing:

            market_data.sort_values(
                "date",
                inplace=True,
            )

        if not signals[
            "date"
        ].is_monotonic_increasing:

            signals.sort_values(
                "date",
                inplace=True,
            )

        # =====================================================
        # Symbol Consistency
        # =====================================================

        market_symbols = set(
            market_data["symbol"]
        )

        signal_symbols = set(
            signals["symbol"]
        )

        unknown = (
            signal_symbols
            - market_symbols
        )

        if unknown:

            raise ValueError(

                "Signals reference "
                f"unknown symbols: "
                f"{sorted(list(unknown))[:20]}"

            )

        # =====================================================
        # Configuration Validation
        # =====================================================

        if (
            self.config.initial_capital
            <= 0
        ):

            raise ValueError(
                "Initial capital must be positive."
            )

        if (
            self.config.max_positions
            <= 0
        ):

            raise ValueError(
                "max_positions must be positive."
            )

        if not (
            0
            < self.config.max_position_weight
            <= 1
        ):

            raise ValueError(
                "Invalid max_position_weight."
            )

        if (
            self.config.rebalance_frequency
            not in {
                "Daily",
                "Weekly",
                "Monthly",
                "Quarterly",
            }
        ):

            raise ValueError(
                "Invalid rebalance frequency."
            )

        logger.info(
            "Input validation completed successfully."
        )



    def _simulate(
        self,
        market_data: pd.DataFrame,
        signals: pd.DataFrame,
    ) -> dict[str, pd.DataFrame]:
        """
        Run the portfolio simulation.

        Returns
        -------
        dict
            Simulation outputs.
        """

        logger.info(
            "Starting portfolio simulation."
        )

        # -----------------------------------------------------
        # Initialize State
        # -----------------------------------------------------

        cash = self.config.initial_capital

        portfolio_value = cash

        positions = {}

        equity_curve = []

        trade_log = []

        order_log = []

        portfolio_history = []

        # -----------------------------------------------------
        # Trading Calendar
        # -----------------------------------------------------

        trading_dates = (
            market_data["date"]
            .drop_duplicates()
            .sort_values()
        )

        # -----------------------------------------------------
        # Simulation Loop
        # -----------------------------------------------------

        for current_date in trading_dates:

            daily_market = market_data[
                market_data["date"] == current_date
            ]

            daily_signals = signals[
                signals["date"] == current_date
            ]

            # ---------------------------------------------
            # Portfolio Valuation
            # ---------------------------------------------

            portfolio_value = (
                self._mark_to_market(
                    positions,
                    daily_market,
                    cash,
                )
            )

            # ---------------------------------------------
            # Rebalance
            # ---------------------------------------------

            if self._should_rebalance(
                current_date,
            ):

                orders = self._generate_orders(
                    positions=positions,
                    signals=daily_signals,
                    market_data=daily_market,
                    portfolio_value=portfolio_value,
                )

                executed_orders = (
                    self._execute_orders(
                        orders,
                        daily_market,
                    )
                )

                (
                    positions,
                    cash,
                    trades,
                ) = self._update_positions(
                    positions=positions,
                    cash=cash,
                    executions=executed_orders,
                )

                trade_log.extend(
                    trades
                )

                order_log.extend(
                    executed_orders
                )

            # ---------------------------------------------
            # Portfolio Snapshot
            # ---------------------------------------------

            portfolio_history.append(

                self._portfolio_snapshot(
                    current_date=current_date,
                    positions=positions,
                    cash=cash,
                    portfolio_value=portfolio_value,
                )

            )

            equity_curve.append(

                {
                    "date": current_date,
                    "portfolio_value": portfolio_value,
                    "cash": cash,
                    "invested": (
                        portfolio_value
                        - cash
                    ),
                }

            )

        logger.info(
            "Simulation complete."
        )

        return {

            "equity_curve": pd.DataFrame(
                equity_curve,
            ),

            "portfolio_history": pd.DataFrame(
                portfolio_history,
            ),

            "trades": pd.DataFrame(
                trade_log,
            ),

            "orders": pd.DataFrame(
                order_log,
            ),

            "positions": self._positions_dataframe(
                positions,
            ),

            "benchmark": self._benchmark_returns(
                trading_dates,
            ),

            "drawdowns": self._drawdown_report(
                equity_curve,
            ),

            "monthly_returns": self._monthly_returns(
                equity_curve,
            ),

            "yearly_returns": self._yearly_returns(
                equity_curve,
            ),

            "attribution": self._performance_attribution(
                positions,
            ),

        }

    def _should_rebalance(
        self,
        current_date: pd.Timestamp,
    ) -> bool:
        """
        Determine whether the portfolio should rebalance.

        Parameters
        ----------
        current_date : pd.Timestamp
            Current trading date.

        Returns
        -------
        bool
        """

        frequency = (
            self.config.rebalance_frequency.lower()
        )

        # ---------------------------------------------
        # First Trading Day
        # ---------------------------------------------

        if not hasattr(
            self,
            "_last_rebalance_date",
        ):

            self._last_rebalance_date = (
                current_date
            )

            return True

        last = self._last_rebalance_date

        rebalance = False

        # ---------------------------------------------
        # Daily
        # ---------------------------------------------

        if frequency == "daily":

            rebalance = True

        # ---------------------------------------------
        # Weekly
        # ---------------------------------------------

        elif frequency == "weekly":

            rebalance = (
                current_date.isocalendar().week
                != last.isocalendar().week
            )

        # ---------------------------------------------
        # Monthly
        # ---------------------------------------------

        elif frequency == "monthly":

            rebalance = (

                current_date.month
                != last.month

                or

                current_date.year
                != last.year

            )

        # ---------------------------------------------
        # Quarterly
        # ---------------------------------------------

        elif frequency == "quarterly":

            current_quarter = (
                (current_date.month - 1) // 3
            )

            last_quarter = (
                (last.month - 1) // 3
            )

            rebalance = (

                current_quarter
                != last_quarter

                or

                current_date.year
                != last.year

            )

        else:

            raise ValueError(

                "Unsupported rebalance frequency: "
                f"{self.config.rebalance_frequency}"

            )

        if rebalance:

            self._last_rebalance_date = (
                current_date
            )

        return rebalance
       
    def _mark_to_market(
        self,
        positions: dict[str, dict[str, Any]],
        market_data: pd.DataFrame,
        cash: float,
    ) -> float:
        """
        Mark portfolio positions to current market prices.

        Parameters
        ----------
        positions
            Current portfolio positions.
        market_data
            Current day's market data.
        cash
            Available cash.

        Returns
        -------
        float
            Portfolio Net Asset Value (NAV).
        """

        portfolio_value = cash

        if not positions:

            return portfolio_value

        # -----------------------------------------------------
        # Current Prices
        # -----------------------------------------------------

        current_prices = (
            market_data
            .set_index("symbol")["close"]
            .to_dict()
        )

        # -----------------------------------------------------
        # Mark-to-Market
        # -----------------------------------------------------

        for symbol, position in positions.items():

            if symbol not in current_prices:

                logger.warning(
                    "Missing market price for %s",
                    symbol,
                )

                continue

            current_price = float(
                current_prices[symbol]
            )

            quantity = float(
                position["quantity"]
            )

            market_value = (
                quantity * current_price
            )

            unrealized_pnl = (
                current_price
                - position["average_price"]
            ) * quantity

            # Update position

            position["last_price"] = current_price

            position["market_value"] = market_value

            position["unrealized_pnl"] = (
                unrealized_pnl
            )

            portfolio_value += market_value

        return float(portfolio_value)

    def _generate_orders(
        self,
        positions: dict[str, dict[str, Any]],
        signals: pd.DataFrame,
        market_data: pd.DataFrame,
        portfolio_value: float,
    ) -> list[dict[str, Any]]:
        """
        Generate portfolio rebalance orders.

        Parameters
        ----------
        positions
            Current portfolio positions.
        signals
            Target portfolio signals.
        market_data
            Current market data.
        portfolio_value
            Current portfolio NAV.

        Returns
        -------
        list[dict]
            Orders to execute.
        """

        logger.info(
            "Generating rebalance orders."
        )

        orders: list[dict[str, Any]] = []

        if signals.empty:

            return orders

        # -----------------------------------------------------
        # Market Prices
        # -----------------------------------------------------

        prices = (
            market_data
            .set_index("symbol")["close"]
            .to_dict()
        )

        # -----------------------------------------------------
        # Normalize Target Weights
        # -----------------------------------------------------

        signals = signals.copy()

        if "weight" not in signals.columns:

            if "score" in signals.columns:

                total_score = (
                    signals["score"]
                    .clip(lower=0)
                    .sum()
                )

                if total_score > 0:

                    signals["weight"] = (
                        signals["score"]
                        / total_score
                    )

                else:

                    equal_weight = (
                        1.0 / len(signals)
                    )

                    signals["weight"] = (
                        equal_weight
                    )

            else:

                equal_weight = (
                    1.0 / len(signals)
                )

                signals["weight"] = (
                    equal_weight
                )

        # -----------------------------------------------------
        # Position Limits
        # -----------------------------------------------------

        signals["weight"] = signals[
            "weight"
        ].clip(
            upper=self.config.max_position_weight
        )

        total_weight = (
            signals["weight"].sum()
        )

        if total_weight > 0:

            signals["weight"] /= total_weight

        # -----------------------------------------------------
        # Generate Orders
        # -----------------------------------------------------

        for _, row in signals.iterrows():

            symbol = row["symbol"]

            if symbol not in prices:

                continue

            price = float(
                prices[symbol]
            )

            target_weight = float(
                row["weight"]
            )

            target_value = (
                portfolio_value
                * target_weight
            )

            target_quantity = (
                target_value / price
            )

            if (
                not self.config.allow_fractional_shares
            ):

                target_quantity = int(
                    target_quantity
                )

            current_quantity = (
                positions
                .get(symbol, {})
                .get("quantity", 0)
            )

            order_quantity = (
                target_quantity
                - current_quantity
            )

            if order_quantity == 0:

                continue

            side = (
                "BUY"
                if order_quantity > 0
                else "SELL"
            )

            orders.append(

                {

                    "date": row["date"],

                    "symbol": symbol,

                    "side": side,

                    "quantity": abs(
                        order_quantity
                    ),

                    "price": price,

                    "target_weight": target_weight,

                    "order_value": abs(
                        order_quantity
                    )
                    * price,

                }

            )

        # -----------------------------------------------------
        # Liquidate Removed Positions
        # -----------------------------------------------------

        target_symbols = set(
            signals["symbol"]
        )

        for symbol, position in positions.items():

            if symbol in target_symbols:

                continue

            if symbol not in prices:

                continue

            quantity = position[
                "quantity"
            ]

            if quantity <= 0:

                continue

            orders.append(

                {

                    "date": signals[
                        "date"
                    ].iloc[0],

                    "symbol": symbol,

                    "side": "SELL",

                    "quantity": quantity,

                    "price": prices[symbol],

                    "target_weight": 0.0,

                    "order_value": (
                        quantity
                        * prices[symbol]
                    ),

                }

            )

        logger.info(
            "Generated %d orders.",
            len(orders),
        )

        return orders

    def _execute_orders(
        self,
        orders: list[dict[str, Any]],
        market_data: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Simulate execution of portfolio orders.

        Parameters
        ----------
        orders
            Generated rebalance orders.
        market_data
            Current market data.

        Returns
        -------
        list[dict]
            Executed orders.
        """

        logger.info(
            "Executing %d orders.",
            len(orders),
        )

        executed_orders: list[dict[str, Any]] = []

        if not orders:

            return executed_orders

        # -----------------------------------------------------
        # Current Prices
        # -----------------------------------------------------

        prices = (
            market_data
            .set_index("symbol")["close"]
            .to_dict()
        )

        for order in orders:

            symbol = order["symbol"]

            if symbol not in prices:

                logger.warning(
                    "No market price for %s",
                    symbol,
                )

                continue

            market_price = float(
                prices[symbol]
            )

            side = order["side"]

            quantity = float(
                order["quantity"]
            )

            # -------------------------------------------------
            # Slippage
            # -------------------------------------------------

            if side == "BUY":

                execution_price = (
                    market_price
                    * (
                        1
                        + self.config.slippage
                    )
                )

            else:

                execution_price = (
                    market_price
                    * (
                        1
                        - self.config.slippage
                    )
                )

            # -------------------------------------------------
            # Execution Value
            # -------------------------------------------------

            execution_value = (
                quantity
                * execution_price
            )

            # -------------------------------------------------
            # Transaction Costs
            # -------------------------------------------------

            brokerage = (
                execution_value
                * self.config.brokerage
            )

            exchange_fee = (
                execution_value
                * self.config.exchange_fee
            )

            taxes = (
                execution_value
                * self.config.taxes
            )

            market_impact = (
                execution_value
                * self.config.market_impact
            )

            total_cost = (

                brokerage

                + exchange_fee

                + taxes

                + market_impact

            )

            # -------------------------------------------------
            # Executed Order
            # -------------------------------------------------

            executed_orders.append(

                {

                    **order,

                    "market_price": market_price,

                    "execution_price": execution_price,

                    "executed_quantity": quantity,

                    "execution_value": execution_value,

                    "brokerage": brokerage,

                    "exchange_fee": exchange_fee,

                    "taxes": taxes,

                    "market_impact": market_impact,

                    "transaction_cost": total_cost,

                    "slippage_cost": abs(
                        execution_price
                        - market_price
                    )
                    * quantity,

                    "status": "FILLED",

                }

            )

        logger.info(

            "Executed %d orders.",

            len(executed_orders),

        )

        return executed_orders

    def _update_positions(
        self,
        positions: dict[str, dict[str, Any]],
        cash: float,
        executions: list[dict[str, Any]],
    ) -> tuple[
        dict[str, dict[str, Any]],
        float,
        list[dict[str, Any]],
    ]:
        """
        Update portfolio positions after execution.

        Parameters
        ----------
        positions
            Current portfolio positions.
        cash
            Available cash.
        executions
            Executed orders.

        Returns
        -------
        tuple
            Updated positions, cash, and trade ledger.
        """

        logger.info(
            "Updating portfolio positions."
        )

        trade_log: list[dict[str, Any]] = []

        updated_positions = positions.copy()

        for execution in executions:

            symbol = execution["symbol"]

            side = execution["side"]

            quantity = float(
                execution["executed_quantity"]
            )

            price = float(
                execution["execution_price"]
            )

            transaction_cost = float(
                execution["transaction_cost"]
            )

            trade_value = (
                quantity * price
            )

            # =================================================
            # BUY
            # =================================================

            if side == "BUY":

                total_cost = (
                    trade_value
                    + transaction_cost
                )

                cash -= total_cost

                if symbol not in updated_positions:

                    updated_positions[symbol] = {

                        "symbol": symbol,

                        "quantity": quantity,

                        "average_price": price,

                        "last_price": price,

                        "market_value": trade_value,

                        "unrealized_pnl": 0.0,

                        "realized_pnl": 0.0,

                        "entry_date": execution["date"],

                    }

                else:

                    position = updated_positions[
                        symbol
                    ]

                    old_qty = position[
                        "quantity"
                    ]

                    old_avg = position[
                        "average_price"
                    ]

                    new_qty = (
                        old_qty + quantity
                    )

                    new_avg = (

                        old_qty * old_avg

                        + quantity * price

                    ) / new_qty

                    position["quantity"] = (
                        new_qty
                    )

                    position[
                        "average_price"
                    ] = new_avg

            # =================================================
            # SELL
            # =================================================

            elif side == "SELL":

                if symbol not in updated_positions:

                    continue

                position = updated_positions[
                    symbol
                ]

                sell_qty = min(
                    quantity,
                    position["quantity"],
                )

                realized_pnl = (

                    price
                    - position["average_price"]

                ) * sell_qty

                proceeds = (

                    sell_qty * price

                    - transaction_cost

                )

                cash += proceeds

                position["quantity"] -= sell_qty

                position[
                    "realized_pnl"
                ] = (

                    position.get(
                        "realized_pnl",
                        0.0,
                    )

                    + realized_pnl

                )

                if (
                    position["quantity"]
                    <= 0
                ):

                    del updated_positions[
                        symbol
                    ]

            # =================================================
            # Trade Record
            # =================================================

            trade_log.append(

                {

                    "date": execution["date"],

                    "symbol": symbol,

                    "side": side,

                    "quantity": quantity,

                    "price": price,

                    "trade_value": trade_value,

                    "transaction_cost": transaction_cost,

                    "cash_after_trade": cash,

                    "status": execution[
                        "status"
                    ],

                }

            )

        logger.info(

            "Portfolio now contains %d positions.",

            len(updated_positions),

        )

        return (

            updated_positions,

            cash,

            trade_log,

        )

    def _portfolio_snapshot(
        self,
        current_date: pd.Timestamp,
        positions: dict[str, dict[str, Any]],
        cash: float,
        portfolio_value: float,
    ) -> dict[str, Any]:
        """
        Create an end-of-day portfolio snapshot.

        Parameters
        ----------
        current_date
            Current trading date.
        positions
            Portfolio positions.
        cash
            Available cash.
        portfolio_value
            Portfolio NAV.

        Returns
        -------
        dict
            Portfolio snapshot.
        """

        invested_value = sum(
            position.get("market_value", 0.0)
            for position in positions.values()
        )

        gross_exposure = (
            invested_value / portfolio_value
            if portfolio_value > 0
            else 0.0
        )

        net_exposure = gross_exposure

        cash_weight = (
            cash / portfolio_value
            if portfolio_value > 0
            else 0.0
        )

        invested_weight = (
            invested_value / portfolio_value
            if portfolio_value > 0
            else 0.0
        )

        unrealized_pnl = sum(
            position.get(
                "unrealized_pnl",
                0.0,
            )
            for position in positions.values()
        )

        realized_pnl = sum(
            position.get(
                "realized_pnl",
                0.0,
            )
            for position in positions.values()
        )

        largest_position = 0.0

        if invested_value > 0:

            largest_position = max(

                (
                    position["market_value"]
                    / invested_value
                )

                for position in positions.values()

            )

        return {

            "date": current_date,

            "portfolio_value": portfolio_value,

            "cash": cash,

            "invested_value": invested_value,

            "cash_weight": cash_weight,

            "invested_weight": invested_weight,

            "gross_exposure": gross_exposure,

            "net_exposure": net_exposure,

            "position_count": len(
                positions
            ),

            "largest_position_weight":
                largest_position,

            "realized_pnl":
                realized_pnl,

            "unrealized_pnl":
                unrealized_pnl,

            "total_pnl":
                realized_pnl
                + unrealized_pnl,

        }
        

    def _positions_dataframe(
        self,
        positions: dict[str, dict[str, Any]],
    ) -> pd.DataFrame:
        """
        Convert portfolio positions to a DataFrame.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        pd.DataFrame
            Positions DataFrame.
        """

        if not positions:

            return pd.DataFrame(
                columns=[
                    "symbol",
                    "quantity",
                    "average_price",
                    "last_price",
                    "market_value",
                    "cost_basis",
                    "unrealized_pnl",
                    "realized_pnl",
                    "weight",
                    "entry_date",
                ]
            )

        records: list[dict[str, Any]] = []

        total_market_value = sum(
            position.get("market_value", 0.0)
            for position in positions.values()
        )

        for position in positions.values():

            market_value = float(
                position.get(
                    "market_value",
                    0.0,
                )
            )

            quantity = float(
                position.get(
                    "quantity",
                    0.0,
                )
            )

            average_price = float(
                position.get(
                    "average_price",
                    0.0,
                )
            )

            cost_basis = (
                quantity * average_price
            )

            weight = (
                market_value / total_market_value
                if total_market_value > 0
                else 0.0
            )

            records.append(

                {

                    "symbol":
                        position.get("symbol"),

                    "quantity":
                        quantity,

                    "average_price":
                        average_price,

                    "last_price":
                        position.get(
                            "last_price",
                            np.nan,
                        ),

                    "market_value":
                        market_value,

                    "cost_basis":
                        cost_basis,

                    "weight":
                        weight,

                    "unrealized_pnl":
                        position.get(
                            "unrealized_pnl",
                            0.0,
                        ),

                    "realized_pnl":
                        position.get(
                            "realized_pnl",
                            0.0,
                        ),

                    "entry_date":
                        position.get(
                            "entry_date",
                        ),

                }

            )

        df = pd.DataFrame(records)

        if not df.empty:

            df.sort_values(
                by="market_value",
                ascending=False,
                inplace=True,
            )

            df.reset_index(
                drop=True,
                inplace=True,
            )

        logger.info(
            "Generated positions DataFrame with %d positions.",
            len(df),
        )

        return df


    def _benchmark_returns(
        self,
        trading_dates: pd.Series,
    ) -> pd.DataFrame:
        """
        Generate benchmark return series.

        Parameters
        ----------
        trading_dates
            Trading calendar used by the backtest.

        Returns
        -------
        pd.DataFrame
            Benchmark performance.
        """

        logger.info(
            "Generating benchmark returns."
        )

        if len(trading_dates) == 0:

            return pd.DataFrame(
                columns=[
                    "date",
                    "benchmark_value",
                    "daily_return",
                    "cumulative_return",
                ]
            )

        benchmark = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    trading_dates
                )
            }
        )

        # -----------------------------------------------------
        # Placeholder Benchmark
        # -----------------------------------------------------

        benchmark["benchmark_value"] = (
            self.config.initial_capital
        )

        benchmark["daily_return"] = 0.0

        benchmark["cumulative_return"] = 0.0

        benchmark["benchmark_value"] = (
            benchmark["benchmark_value"]
            * (
                1
                + benchmark["cumulative_return"]
            )
        )

        logger.info(
            "Generated benchmark with %d observations.",
            len(benchmark),
        )

        return benchmark

    def _drawdown_report(
        self,
        equity_curve: list[dict[str, Any]] | pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate portfolio drawdown report.

        Parameters
        ----------
        equity_curve
            Portfolio equity curve.

        Returns
        -------
        pd.DataFrame
            Drawdown analytics.
        """

        logger.info(
            "Calculating drawdown report."
        )

        if isinstance(
            equity_curve,
            list,
        ):

            equity_curve = pd.DataFrame(
                equity_curve,
            )

        if equity_curve.empty:

            return pd.DataFrame(
                columns=[
                    "date",
                    "portfolio_value",
                    "running_peak",
                    "drawdown",
                    "drawdown_pct",
                    "duration",
                ]
            )

        df = equity_curve.copy()

        df = df.sort_values(
            "date"
        ).reset_index(
            drop=True
        )

        # -----------------------------------------------------
        # Running Peak
        # -----------------------------------------------------

        df["running_peak"] = (
            df["portfolio_value"]
            .cummax()
        )

        # -----------------------------------------------------
        # Drawdown
        # -----------------------------------------------------

        df["drawdown"] = (

            df["portfolio_value"]

            - df["running_peak"]

        )

        df["drawdown_pct"] = np.where(

            df["running_peak"] > 0,

            df["drawdown"]
            / df["running_peak"],

            0.0,

        )

        # -----------------------------------------------------
        # Drawdown Duration
        # -----------------------------------------------------

        durations = []

        current_duration = 0

        for value in df["drawdown_pct"]:

            if value < 0:

                current_duration += 1

            else:

                current_duration = 0

            durations.append(
                current_duration
            )

        df["duration"] = durations

        logger.info(

            "Maximum drawdown: %.2f%%",

            abs(
                df["drawdown_pct"].min()
            )
            * 100,

        )

        return df[
            [
                "date",
                "portfolio_value",
                "running_peak",
                "drawdown",
                "drawdown_pct",
                "duration",
            ]
        ]

    def _monthly_returns(
        self,
        equity_curve: list[dict[str, Any]] | pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate monthly portfolio returns.

        Parameters
        ----------
        equity_curve
            Portfolio equity curve.

        Returns
        -------
        pd.DataFrame
            Monthly return statistics.
        """

        logger.info(
            "Calculating monthly returns."
        )

        if isinstance(
            equity_curve,
            list,
        ):

            equity_curve = pd.DataFrame(
                equity_curve,
            )

        if equity_curve.empty:

            return pd.DataFrame(
                columns=[
                    "year",
                    "month",
                    "month_end_value",
                    "monthly_return",
                ]
            )

        df = equity_curve.copy()

        df["date"] = pd.to_datetime(
            df["date"]
        )

        df = (
            df.sort_values("date")
            .set_index("date")
        )

        # -----------------------------------------------------
        # Month-End Portfolio Value
        # -----------------------------------------------------

        monthly = (
            df["portfolio_value"]
            .resample("ME")
            .last()
            .to_frame(
                name="month_end_value"
            )
        )

        # -----------------------------------------------------
        # Monthly Returns
        # -----------------------------------------------------

        monthly["monthly_return"] = (
            monthly["month_end_value"]
            .pct_change()
            .fillna(0.0)
        )

        monthly["year"] = (
            monthly.index.year
        )

        monthly["month"] = (
            monthly.index.month
        )

        monthly.reset_index(
            inplace=True,
        )

        monthly.rename(
            columns={
                "date": "month_end",
            },
            inplace=True,
        )

        logger.info(
            "Generated %d monthly observations.",
            len(monthly),
        )

        return monthly[
            [
                "month_end",
                "year",
                "month",
                "month_end_value",
                "monthly_return",
            ]
        ]

    def _yearly_returns(
        self,
        equity_curve: list[dict[str, Any]] | pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate yearly portfolio returns.

        Parameters
        ----------
        equity_curve
            Portfolio equity curve.

        Returns
        -------
        pd.DataFrame
            Yearly return statistics.
        """

        logger.info(
            "Calculating yearly returns."
        )

        if isinstance(
            equity_curve,
            list,
        ):

            equity_curve = pd.DataFrame(
                equity_curve,
            )

        if equity_curve.empty:

            return pd.DataFrame(
                columns=[
                    "year",
                    "year_end_value",
                    "yearly_return",
                ]
            )

        df = equity_curve.copy()

        df["date"] = pd.to_datetime(
            df["date"]
        )

        df = (
            df.sort_values("date")
            .set_index("date")
        )

        # -----------------------------------------------------
        # Year-End Portfolio Value
        # -----------------------------------------------------

        yearly = (
            df["portfolio_value"]
            .resample("YE")
            .last()
            .to_frame(
                name="year_end_value"
            )
        )

        # -----------------------------------------------------
        # Yearly Returns
        # -----------------------------------------------------

        yearly["yearly_return"] = (
            yearly["year_end_value"]
            .pct_change()
            .fillna(0.0)
        )

        yearly["year"] = (
            yearly.index.year
        )

        yearly.reset_index(
            inplace=True,
        )

        yearly.rename(
            columns={
                "date": "year_end",
            },
            inplace=True,
        )

        logger.info(
            "Generated %d yearly observations.",
            len(yearly),
        )

        return yearly[
            [
                "year_end",
                "year",
                "year_end_value",
                "yearly_return",
            ]
        ]

    def _performance_attribution(
        self,
        positions: dict[str, dict[str, Any]],
    ) -> pd.DataFrame:
        """
        Generate portfolio performance attribution.

        Parameters
        ----------
        positions
            Current portfolio positions.

        Returns
        -------
        pd.DataFrame
            Position-level attribution report.
        """

        logger.info(
            "Generating performance attribution."
        )

        if not positions:

            return pd.DataFrame(
                columns=[
                    "symbol",
                    "weight",
                    "quantity",
                    "market_value",
                    "cost_basis",
                    "unrealized_pnl",
                    "realized_pnl",
                    "total_pnl",
                    "contribution",
                ]
            )

        total_market_value = sum(
            position.get(
                "market_value",
                0.0,
            )
            for position in positions.values()
        )

        records: list[dict[str, Any]] = []

        for position in positions.values():

            market_value = float(
                position.get(
                    "market_value",
                    0.0,
                )
            )

            quantity = float(
                position.get(
                    "quantity",
                    0.0,
                )
            )

            average_price = float(
                position.get(
                    "average_price",
                    0.0,
                )
            )

            cost_basis = (
                quantity * average_price
            )

            unrealized_pnl = float(
                position.get(
                    "unrealized_pnl",
                    0.0,
                )
            )

            realized_pnl = float(
                position.get(
                    "realized_pnl",
                    0.0,
                )
            )

            total_pnl = (
                unrealized_pnl
                + realized_pnl
            )

            weight = (
                market_value
                / total_market_value
                if total_market_value > 0
                else 0.0
            )

            contribution = (
                total_pnl
                / total_market_value
                if total_market_value > 0
                else 0.0
            )

            records.append(

                {

                    "symbol":
                        position.get("symbol"),

                    "weight":
                        weight,

                    "quantity":
                        quantity,

                    "market_value":
                        market_value,

                    "cost_basis":
                        cost_basis,

                    "unrealized_pnl":
                        unrealized_pnl,

                    "realized_pnl":
                        realized_pnl,

                    "total_pnl":
                        total_pnl,

                    "contribution":
                        contribution,

                }

            )

        attribution = pd.DataFrame(
            records,
        )

        attribution.sort_values(
            by="contribution",
            ascending=False,
            inplace=True,
        )

        attribution.reset_index(
            drop=True,
            inplace=True,
        )

        logger.info(
            "Generated attribution for %d positions.",
            len(attribution),
        )

        return attribution

                
    def _performance_statistics(
        self,
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
    ) -> BacktestStatistics:
        """
        Calculate institutional performance statistics.

        Parameters
        ----------
        equity_curve
            Portfolio equity curve.
        trades
            Executed trades.

        Returns
        -------
        BacktestStatistics
        """

        logger.info(
            "Calculating performance statistics."
        )

        stats = BacktestStatistics()

        if equity_curve.empty:

            return stats

        df = equity_curve.copy()

        df["date"] = pd.to_datetime(
            df["date"]
        )

        df.sort_values(
            "date",
            inplace=True,
        )

        # -----------------------------------------------------
        # Daily Returns
        # -----------------------------------------------------

        returns = (
            df["portfolio_value"]
            .pct_change()
            .fillna(0.0)
        )

        initial_value = float(
            df["portfolio_value"].iloc[0]
        )

        final_value = float(
            df["portfolio_value"].iloc[-1]
        )

        # -----------------------------------------------------
        # Total Return
        # -----------------------------------------------------

        stats.total_return = (
            (final_value / initial_value) - 1
            if initial_value > 0
            else 0.0
        )

        # -----------------------------------------------------
        # CAGR
        # -----------------------------------------------------

        days = max(
            (
                df["date"].iloc[-1]
                - df["date"].iloc[0]
            ).days,
            1,
        )

        years = days / 365.25

        if years > 0:

            stats.annual_return = (

                (final_value / initial_value)

                ** (1 / years)

                - 1

            )

        # -----------------------------------------------------
        # Volatility
        # -----------------------------------------------------

        stats.annual_volatility = (

            returns.std()

            * np.sqrt(252)

        )

        # -----------------------------------------------------
        # Sharpe Ratio
        # -----------------------------------------------------

        if stats.annual_volatility > 0:

            stats.sharpe_ratio = (

                (
                    stats.annual_return
                    - self.config.risk_free_rate
                )

                / stats.annual_volatility

            )

        # -----------------------------------------------------
        # Sortino Ratio
        # -----------------------------------------------------

        downside = returns[
            returns < 0
        ]

        if len(downside):

            downside_vol = (

                downside.std()

                * np.sqrt(252)

            )

            if downside_vol > 0:

                stats.sortino_ratio = (

                    (
                        stats.annual_return
                        - self.config.risk_free_rate
                    )

                    / downside_vol

                )

        # -----------------------------------------------------
        # Maximum Drawdown
        # -----------------------------------------------------

        running_max = (
            df["portfolio_value"]
            .cummax()
        )

        drawdown = (

            df["portfolio_value"]

            - running_max

        ) / running_max

        stats.max_drawdown = abs(
            drawdown.min()
        )

        # -----------------------------------------------------
        # Calmar Ratio
        # -----------------------------------------------------

        if stats.max_drawdown > 0:

            stats.calmar_ratio = (

                stats.annual_return

                / stats.max_drawdown

            )

        # -----------------------------------------------------
        # Value at Risk
        # -----------------------------------------------------

        stats.value_at_risk = np.percentile(
            returns,
            5,
        )

        # -----------------------------------------------------
        # Expected Shortfall
        # -----------------------------------------------------

        tail = returns[
            returns <= stats.value_at_risk
        ]

        if len(tail):

            stats.expected_shortfall = (
                tail.mean()
            )

        # -----------------------------------------------------
        # Trade Statistics
        # -----------------------------------------------------

        if not trades.empty:

            stats.total_trades = len(
                trades
            )

            pnl = (

                trades["trade_value"]

                - trades["transaction_cost"]

            )

            winners = pnl > 0

            losers = pnl < 0

            stats.winning_trades = int(
                winners.sum()
            )

            stats.losing_trades = int(
                losers.sum()
            )

            if stats.total_trades > 0:

                stats.win_rate = (

                    stats.winning_trades

                    / stats.total_trades

                )

            if winners.any():

                stats.average_win = (
                    pnl[winners].mean()
                )

            if losers.any():

                stats.average_loss = abs(
                    pnl[losers].mean()
                )

            if stats.average_loss > 0:

                stats.profit_factor = (

                    pnl[winners].sum()

                    / abs(
                        pnl[losers].sum()
                    )

                )

            stats.expectancy = (

                stats.win_rate
                * stats.average_win

                -

                (
                    1
                    - stats.win_rate
                )
                * stats.average_loss

            )

            stats.execution_cost = (
                trades[
                    "transaction_cost"
                ].sum()
            )

        # -----------------------------------------------------
        # Exposure
        # -----------------------------------------------------

        invested = (
            df["portfolio_value"]
            - df["cash"]
        )

        stats.exposure = (

            invested

            / df["portfolio_value"]

        ).mean()

        logger.info(
            "Performance statistics calculated."
        )

        return stats

    
    def _build_result(
        self,
        simulation: dict[str, Any],
        statistics: BacktestStatistics,
    ) -> BacktestResult:
        """
        Build the final institutional backtest result.

        Parameters
        ----------
        simulation
            Simulation outputs.
        statistics
            Calculated performance statistics.

        Returns
        -------
        BacktestResult
        """

        logger.info(
            "Building backtest result."
        )

        result = BacktestResult(

            equity_curve=simulation.get(
                "equity_curve",
                pd.DataFrame(),
            ),

            portfolio_history=simulation.get(
                "portfolio_history",
                pd.DataFrame(),
            ),

            trades=simulation.get(
                "trades",
                pd.DataFrame(),
            ),

            positions=simulation.get(
                "positions",
                pd.DataFrame(),
            ),

            orders=simulation.get(
                "orders",
                pd.DataFrame(),
            ),

            benchmark=simulation.get(
                "benchmark",
                pd.DataFrame(),
            ),

            drawdowns=simulation.get(
                "drawdowns",
                pd.DataFrame(),
            ),

            monthly_returns=simulation.get(
                "monthly_returns",
                pd.DataFrame(),
            ),

            yearly_returns=simulation.get(
                "yearly_returns",
                pd.DataFrame(),
            ),

            attribution=simulation.get(
                "attribution",
                pd.DataFrame(),
            ),

            statistics=statistics,

            metadata={

                "engine": self.__class__.__name__,

                "version": "1.0.0",

                "initial_capital":
                    self.config.initial_capital,

                "benchmark":
                    self.config.benchmark_symbol,

                "rebalance_frequency":
                    self.config.rebalance_frequency,

                "execution_model":
                    self.config.execution_model,

            },

        )

        logger.info(
            "Backtest result created successfully."
        )

        return result
    

_BACKTEST_ENGINE = BacktestEngine()


def run_backtest(
    market_data: pd.DataFrame,
    signals: pd.DataFrame,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    """
    Run institutional backtest.
    """

    engine = (
        _BACKTEST_ENGINE
        if config is None
        else BacktestEngine(config)
    )

    return engine.run(
        market_data,
        signals,
    )


__all__ = [
    "BacktestStatistics",
    "BacktestResult",
    "BacktestEngine",
    "run_backtest",
]