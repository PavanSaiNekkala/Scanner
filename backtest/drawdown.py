"""
drawdown.py
===========

Institutional Drawdown Analytics Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DrawdownConfig:
    """
    Drawdown analysis configuration.
    """

    annualization_factor: int = 252


class DrawdownEngine:
    """
    Institutional drawdown analytics engine.
    """

    def __init__(
        self,
        config: DrawdownConfig,
    ) -> None:
        """
        Initialize drawdown engine.
        """

        self.config = config

        logger.info(
            "DrawdownEngine initialized."
        )

    def equity_curve(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Compute equity curve.
        """

        returns = returns.fillna(
            0.0
        )

        return (
            1.0 + returns
        ).cumprod()

    def running_peak(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Compute running equity peak.
        """

        equity = self.equity_curve(
            returns
        )

        return equity.cummax()

    def drawdown(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Compute drawdown series.
        """

        equity = self.equity_curve(
            returns
        )

        peak = equity.cummax()

        return (
            equity
            / peak
            - 1.0
        )

    def maximum_drawdown(
        self,
        returns: pd.Series,
    ) -> float:
        """
        Compute maximum drawdown.
        """

        return float(
            self.drawdown(
                returns
            ).min()
        )

    def drawdown_duration(
        self,
        returns: pd.Series,
    ) -> int:
        """
        Compute longest drawdown duration.
        """

        drawdown = self.drawdown(
            returns
        )

        duration = 0

        maximum = 0

        for value in drawdown:

            if value < 0:

                duration += 1

                maximum = max(
                    maximum,
                    duration,
                )

            else:

                duration = 0

        return maximum


    def recovery_time(
        self,
        returns: pd.Series,
    ) -> int:
        """
        Compute recovery time from the maximum drawdown.
        """

        equity = self.equity_curve(
            returns
        )

        running_peak = (
            equity.cummax()
        )

        drawdown = (
            equity
            / running_peak
            - 1.0
        )

        trough = drawdown.idxmin()

        previous_peak = (
            running_peak.loc[
                trough
            ]
        )

        recovery = equity.loc[
            trough:
        ]

        recovered = recovery[
            recovery >= previous_peak
        ]

        if recovered.empty:
            return -1

        return int(
            equity.index.get_loc(
                recovered.index[0]
            )
            - equity.index.get_loc(
                trough
            )
        )

    def underwater_curve(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Return the underwater curve.
        """

        return self.drawdown(
            returns
        )

    def drawdown_periods(
        self,
        returns: pd.Series,
    ) -> pd.DataFrame:
        """
        Return drawdown periods.
        """

        drawdown = self.drawdown(
            returns
        )

        periods: list[
            dict[str, object]
        ] = []

        start = None

        minimum = 0.0

        trough = None

        for date, value in drawdown.items():

            if value < 0:

                if start is None:

                    start = date

                    minimum = value

                    trough = date

                elif value < minimum:

                    minimum = value

                    trough = date

            elif start is not None:

                periods.append(
                    {
                        "start": start,
                        "trough": trough,
                        "end": date,
                        "drawdown": minimum,
                    }
                )

                start = None

                minimum = 0.0

                trough = None

        if start is not None:

            periods.append(
                {
                    "start": start,
                    "trough": trough,
                    "end": None,
                    "drawdown": minimum,
                }
            )

        return pd.DataFrame(
            periods
        )

    def summary(
        self,
        returns: pd.Series,
    ) -> pd.Series:
        """
        Return drawdown summary statistics.
        """

        return pd.Series(
            {
                "Maximum Drawdown":
                self.maximum_drawdown(
                    returns
                ),
                "Drawdown Duration":
                self.drawdown_duration(
                    returns
                ),
                "Recovery Time":
                self.recovery_time(
                    returns
                ),
            }
        )

    def reset(
        self,
    ) -> None:
        """
        Reset drawdown engine.
        """

        logger.info(
            "DrawdownEngine reset."
        )