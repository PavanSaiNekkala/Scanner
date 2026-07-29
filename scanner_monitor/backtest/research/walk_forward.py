"""
walk_forward.py
===============

Institutional Walk-Forward Analysis Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

import logging
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WalkForwardConfig:
    """
    Configuration for walk-forward analysis.
    """

    train_period: int = 252 * 2

    test_period: int = 63

    step_size: int = 63

    expanding_window: bool = False

    minimum_observations: int = 500


class WalkForwardEngine:
    """
    Institutional Walk-Forward Analysis Engine.
    """

    def __init__(
        self,
        config: WalkForwardConfig,
    ) -> None:

        self.config = config

        self.results: list[dict] = []

        logger.info(
            "WalkForwardEngine initialized."
        )


    def generate_windows(
        self,
        data: pd.DataFrame,
    ) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Generate train/test windows.
        """

        windows = []

        start = 0

        while (
            start
            + self.config.train_period
            + self.config.test_period
            <= len(data)
        ):

            train_end = (
                start
                + self.config.train_period
            )

            test_end = (
                train_end
                + self.config.test_period
            )

            if self.config.expanding_window:

                train = data.iloc[
                    :train_end
                ]

            else:

                train = data.iloc[
                    start:train_end
                ]

            test = data.iloc[
                train_end:test_end
            ]

            windows.append(
                (
                    train,
                    test,
                )
            )

            start += self.config.step_size

        return windows

    def run(
        self,
        data: pd.DataFrame,
        strategy,
    ) -> list[dict]:
        """
        Execute walk-forward analysis.
        """

        self.results.clear()

        windows = self.generate_windows(
            data,
        )

        for train, test in windows:

            model = strategy.fit(
                train,
            )

            metrics = model.evaluate(
                test,
            )

            self.results.append(
                metrics
            )

        return self.results

    def summary(
        self,
    ) -> pd.DataFrame:
        """
        Summary of all walk-forward results.
        """

        return pd.DataFrame(
            self.results
        )

    def reset(
        self,
    ) -> None:
        """
        Reset analysis results.
        """

        self.results.clear()

        logger.info(
            "WalkForwardEngine reset."
        )