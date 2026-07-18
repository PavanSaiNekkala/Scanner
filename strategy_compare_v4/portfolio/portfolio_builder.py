"""
=============================================================
Institutional Strategy Comparison Platform V4

Module
------
portfolio/portfolio_builder.py

Purpose
-------
Construct an institutional-grade portfolio using
the outputs from the Strategy Comparison Engine.

Features
--------
• Portfolio Construction
• Position Sizing
• Equal Weight Portfolio
• Score Weighted Portfolio
• Risk Filter
• Recommendation Filter
• Portfolio Summary

=============================================================
"""

from __future__ import annotations

import time
from typing import Dict

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    COMPOSITE_SCORE,
    EXPECTANCY,
    PROFIT_FACTOR,
    RECOMMENDATION,
)

from strategy_compare_v4.config.thresholds import (
    MAX_POSITION_WEIGHT,
)

from strategy_compare_v4.utils.helpers import (
    require_columns,
)

from strategy_compare_v4.utils.math_utils import (
    safe_divide,
    round_dataframe,
)

from strategy_compare_v4.utils.logger import (
    get_logger,
    banner,
)

logger = get_logger(__name__)


# ============================================================
# Portfolio Builder
# ============================================================

class PortfolioBuilder:
    """
    Institutional Portfolio Builder.

    Responsibilities
    ----------------
    • Portfolio construction
    • Position sizing
    • Capital allocation
    • Diversification checks
    • Sector exposure analysis
    • Portfolio reporting
    """

    def __init__(
        self,
        comparison_df: pd.DataFrame,
    ):

        self.df = comparison_df.copy()

        self.filtered = pd.DataFrame()

        self.portfolio = pd.DataFrame()

        self.summary = pd.DataFrame()

        self.sector_summary = pd.DataFrame()

        self.diagnostic_report: Dict = {}

        self.execution_time: float = 0.0

    # ---------------------------------------------------------
    # Validate Input
    # ---------------------------------------------------------

    def validate(self):

        """
        Validate comparison dataframe.
        """

        banner(

            logger,

            "Validating Portfolio Builder Input",

        )

        require_columns(

            self.df,

            [

                "Stock",

                "Strategy",

                COMPOSITE_SCORE,

                RECOMMENDATION,

            ],

        )

        logger.info(

            "Validation successful."

        )

        logger.info(

            "Rows       : %d",

            len(

                self.df,

            ),

        )

        logger.info(

            "Stocks     : %d",

            self.df[

                "Stock"

            ].nunique(),

        )

        logger.info(

            "Strategies : %d",

            self.df[

                "Strategy"

            ].nunique(),

        )

        logger.info(

            "Average Composite : %.2f",

            self.df[

                COMPOSITE_SCORE

            ].mean(),

        )

        return self
    
    # ---------------------------------------------------------
    # Recommendation Filter
    # ---------------------------------------------------------

    def recommendation_filter(
        self,
        recommendations: tuple = (
            "Strong Buy",
            "Buy",
            "Watch",
        ),
    ):
        """
        Filter portfolio candidates
        based on recommendations.
        """

        self.filtered = (

            self.df.loc[

                self.df[

                    RECOMMENDATION

                ].isin(

                    recommendations,

                )

            ]

            .copy()

        )

        logger.info(

            "Recommendation Filter"

        )

        logger.info(

            "Selected Stocks : %d",

            len(

                self.filtered,

            ),

        )

        return self


    # ---------------------------------------------------------
    # Top-N Selection
    # ---------------------------------------------------------

    def top_n(
        self,
        n: int = 25,
    ):
        """
        Select the highest-ranked
        portfolio opportunities.
        """

        self.filtered = (

            self.filtered

            .sort_values(

                COMPOSITE_SCORE,

                ascending=False,

            )

            .head(

                n,

            )

            .reset_index(

                drop=True,

            )

        )

        logger.info(

            "Top %d opportunities selected.",

            n,

        )

        return self


    # ---------------------------------------------------------
    # Equal Weight Portfolio
    # ---------------------------------------------------------

    def equal_weight_portfolio(
        self,
    ):
        """
        Generate an equal-weight
        portfolio.
        """

        self.portfolio = (

            self.filtered

            .copy()

        )

        total_positions = len(

            self.portfolio,

        )

        if total_positions == 0:

            logger.warning(

                "No securities available."

            )

            self.portfolio[

                "Weight %"

            ] = pd.Series(

                dtype=float,

            )

            return self

        self.portfolio[

            "Weight %"

        ] = round(

            100

            / total_positions,

            2,

        )

        self.portfolio = round_dataframe(

            self.portfolio,

            decimals=2,

        )

        logger.info(

            "Equal-weight portfolio created."

        )

        return self


    # ---------------------------------------------------------
    # Composite Score Allocation
    # ---------------------------------------------------------

    def score_weight_portfolio(
        self,
    ):
        """
        Allocate portfolio weights
        using Composite Score.
        """

        require_columns(

            self.portfolio,

            [

                COMPOSITE_SCORE,

            ],

        )

        total_score = (

            self.portfolio[

                COMPOSITE_SCORE

            ]

            .sum()

        )

        if total_score <= 0:

            logger.warning(

                "Composite Score total is zero."

            )

            self.portfolio[

                "Score Weight %"

            ] = self.portfolio[

                "Weight %"

            ]

            return self

        self.portfolio[

            "Score Weight %"

        ] = (

            safe_divide(

                self.portfolio[

                    COMPOSITE_SCORE

                ],

                total_score,

            )

            * 100

        )

        self.portfolio = round_dataframe(

            self.portfolio,

            decimals=2,

        )

        logger.info(

            "Score-weighted portfolio created."

        )

        logger.info(

            "Total Weight : %.2f%%",

            self.portfolio[

                "Score Weight %"

            ].sum(),

        )

        return self
    
    # ---------------------------------------------------------
    # Capital Allocation
    # ---------------------------------------------------------

    def allocation_amount(
        self,
        capital: float = 100000,
    ):
        """
        Allocate investment capital
        according to score weights.
        """

        require_columns(

            self.portfolio,

            [

                "Score Weight %",

            ],

        )

        self.portfolio[

            "Capital"

        ] = (

            capital

            *

            safe_divide(

                self.portfolio[

                    "Score Weight %"

                ],

                100,

            )

        )

        self.portfolio = round_dataframe(

            self.portfolio,

            decimals=2,

        )

        logger.info(

            "Capital allocation completed."

        )

        logger.info(

            "Portfolio Capital : %.2f",

            self.portfolio[

                "Capital"

            ].sum(),

        )

        return self


    # ---------------------------------------------------------
    # Position Ranking
    # ---------------------------------------------------------

    def position_rank(
        self,
    ):
        """
        Rank portfolio positions
        by Composite Score.
        """

        self.portfolio = (

            self.portfolio

            .sort_values(

                COMPOSITE_SCORE,

                ascending=False,

            )

            .reset_index(

                drop=True,

            )

        )

        self.portfolio.insert(

            0,

            "Portfolio Rank",

            np.arange(

                1,

                len(

                    self.portfolio,

                ) + 1,

            ),

        )

        logger.info(

            "Portfolio positions ranked."

        )

        return self


    # ---------------------------------------------------------
    # Portfolio Summary
    # ---------------------------------------------------------

    def portfolio_summary(
        self,
    ):
        """
        Generate portfolio
        summary statistics.
        """

        require_columns(

            self.portfolio,

            [

                COMPOSITE_SCORE,

                EXPECTANCY,

                PROFIT_FACTOR,

                "Capital",

            ],

        )

        self.summary = pd.DataFrame(

            {

                "Metric": [

                    "Positions",

                    "Average Composite",

                    "Average Expectancy",

                    "Average Profit Factor",

                    "Total Capital",

                ],

                "Value": [

                    len(

                        self.portfolio,

                    ),

                    round(

                        self.portfolio[

                            COMPOSITE_SCORE

                        ].mean(),

                        2,

                    ),

                    round(

                        self.portfolio[

                            EXPECTANCY

                        ].mean(),

                        2,

                    ),

                    round(

                        self.portfolio[

                            PROFIT_FACTOR

                        ].mean(),

                        2,

                    ),

                    round(

                        self.portfolio[

                            "Capital"

                        ].sum(),

                        2,

                    ),

                ],

            }

        )

        logger.info(

            "Portfolio summary generated."

        )

        return self


    # ---------------------------------------------------------
    # Diversification Check
    # ---------------------------------------------------------

    def diversification_check(
        self,
    ):
        """
        Calculate portfolio
        diversification metrics.
        """

        require_columns(

            self.portfolio,

            [

                "Score Weight %",

            ],

        )

        self.summary.loc[

            len(

                self.summary,

            )

        ] = [

            "Largest Position (%)",

            round(

                self.portfolio[

                    "Score Weight %"

                ].max(),

                2,

            ),

        ]

        self.summary.loc[

            len(

                self.summary,

            )

        ] = [

            "Smallest Position (%)",

            round(

                self.portfolio[

                    "Score Weight %"

                ].min(),

                2,

            ),

        ]

        self.summary.loc[

            len(

                self.summary,

            )

        ] = [

            "Average Position (%)",

            round(

                self.portfolio[

                    "Score Weight %"

                ].mean(),

                2,

            ),

        ]

        logger.info(

            "Diversification metrics generated."

        )

        return self


    # ---------------------------------------------------------
    # Sector Exposure
    # ---------------------------------------------------------

    def sector_exposure(
        self,
    ):
        """
        Calculate sector-wise
        portfolio exposure.
        """

        if "Sector" not in self.portfolio.columns:

            logger.info(

                "Sector column not available."

            )

            self.sector_summary = pd.DataFrame()

            return self

        self.sector_summary = (

            self.portfolio

            .groupby(

                "Sector",

                as_index=False,

            )

            .agg(

                Positions=(

                    "Stock",

                    "count",

                ),

                Capital=(

                    "Capital",

                    "sum",

                ),

                Weight=(

                    "Score Weight %",

                    "sum",

                ),

            )

            .sort_values(

                "Weight",

                ascending=False,

            )

        )

        self.sector_summary = round_dataframe(

            self.sector_summary,

            decimals=2,

        )

        logger.info(

            "Sector exposure calculated."

        )

        logger.info(

            "Sectors : %d",

            len(

                self.sector_summary,

            ),

        )

        return self


    # ---------------------------------------------------------
    # Position Limit
    # ---------------------------------------------------------

    def apply_position_limit(
        self,
        max_weight: float = MAX_POSITION_WEIGHT,
    ):
        """
        Apply maximum position
        weight constraint.
        """

        require_columns(

            self.portfolio,

            [

                "Score Weight %",

            ],

        )

        self.portfolio[

            "Adjusted Weight %"

        ] = (

            self.portfolio[

                "Score Weight %"

            ]

            .clip(

                upper=max_weight,

            )

        )

        total = (

            self.portfolio[

                "Adjusted Weight %"

            ]

            .sum()

        )

        if total <= 0:

            logger.warning(

                "Adjusted weights sum to zero."

            )

            return self

        self.portfolio[

            "Adjusted Weight %"

        ] = (

            safe_divide(

                self.portfolio[

                    "Adjusted Weight %"

                ],

                total,

            )

            * 100

        )

        self.portfolio = round_dataframe(

            self.portfolio,

            decimals=2,

        )

        logger.info(

            "Maximum position limit applied (%.2f%%).",

            max_weight,

        )

        return self

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    def diagnostics(
        self,
    ):
        """
        Log portfolio diagnostics.
        """

        banner(

            logger,

            "Institutional Portfolio Summary",

        )

        if self.portfolio.empty:

            logger.warning(

                "Portfolio is empty."

            )

            return self

        logger.info(

            "Positions          : %d",

            len(

                self.portfolio,

            ),

        )

        logger.info(

            "Total Capital      : %.2f",

            self.portfolio[

                "Capital"

            ].sum(),

        )

        logger.info(

            "Average Score      : %.2f",

            self.portfolio[

                COMPOSITE_SCORE

            ].mean(),

        )

        if "Adjusted Weight %" in self.portfolio.columns:

            logger.info(

                "Highest Weight     : %.2f%%",

                self.portfolio[

                    "Adjusted Weight %"

                ].max(),

            )

            logger.info(

                "Lowest Weight      : %.2f%%",

                self.portfolio[

                    "Adjusted Weight %"

                ].min(),

            )

        self.diagnostic_report = {

            "positions": len(

                self.portfolio,

            ),

            "capital": round(

                self.portfolio[

                    "Capital"

                ].sum(),

                2,

            ),

            "average_score": round(

                self.portfolio[

                    COMPOSITE_SCORE

                ].mean(),

                2,

            ),

        }

        return self


    # ---------------------------------------------------------
    # Execution Report
    # ---------------------------------------------------------

    def execution_report(
        self,
    ):
        """
        Log execution statistics.
        """

        banner(

            logger,

            "Execution Report",

        )

        logger.info(

            "Execution Time : %.3f seconds",

            self.execution_time,

        )

        return self


    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export(
        self,
        output: str = "Institutional_Portfolio.xlsx",
    ):
        """
        Export portfolio reports.
        """

        from strategy_compare_v4.utils.io_utils import (

            write_excel,

        )

        sheets = {

            "Portfolio":

                self.portfolio,

            "Summary":

                self.summary,

        }

        if not self.sector_summary.empty:

            sheets[

                "Sector Allocation"

            ] = self.sector_summary

        write_excel(

            output,

            sheets,

        )

        logger.info(

            "Portfolio exported to %s",

            output,

        )

        return self


    # ---------------------------------------------------------
    # Get Results
    # ---------------------------------------------------------

    def get_results(
        self,
    ):
        """
        Return generated reports.
        """

        return {

            "portfolio":

                self.portfolio,

            "summary":

                self.summary,

            "sector":

                self.sector_summary,

            "diagnostics":

                self.diagnostic_report,

            "execution_time":

                self.execution_time,

        }


    # ---------------------------------------------------------
    # Run Pipeline
    # ---------------------------------------------------------

    def run(
        self,
        capital: float = 100000,
        top_n: int = 25,
        max_weight: float = MAX_POSITION_WEIGHT,
    ):
        """
        Execute the complete
        portfolio construction
        pipeline.
        """

        start = time.perf_counter()

        try:

            (

                self

                .validate()

                .recommendation_filter()

                .top_n(

                    top_n,

                )

                .equal_weight_portfolio()

                .score_weight_portfolio()

                .allocation_amount(

                    capital,

                )

                .position_rank()

                .portfolio_summary()

                .diversification_check()

                .sector_exposure()

                .apply_position_limit(

                    max_weight,

                )

                .diagnostics()

            )

        except Exception:

            logger.exception(

                "Portfolio construction failed."

            )

            raise

        finally:

            self.execution_time = (

                time.perf_counter()

                - start

            )

            self.execution_report()

        return self


# ============================================================
# Convenience Function
# ============================================================

def build_portfolio(
    comparison_df: pd.DataFrame,
    capital: float = 100000,
    top_n: int = 25,
    max_weight: float = MAX_POSITION_WEIGHT,
    output_file: str = "Institutional_Portfolio.xlsx",
):
    """
    Build an institutional
    portfolio.
    """

    engine = (

        PortfolioBuilder(

            comparison_df,

        )

        .run(

            capital=capital,

            top_n=top_n,

            max_weight=max_weight,

        )

    )

    engine.export(

        output_file,

    )

    return engine


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    from strategy_compare_v4.utils.io_utils import (

        read_excel,

    )

    INPUT_FILE = "strategy_comparison.xlsx"

    OUTPUT_FILE = "Institutional_Portfolio.xlsx"

    try:

        dataframe = read_excel(

            INPUT_FILE,

        )

        build_portfolio(

            dataframe,

            output_file=OUTPUT_FILE,

        )

        logger.info(

            "Portfolio build completed successfully."

        )

    except Exception:

        logger.exception(

            "Portfolio Builder terminated unexpectedly."

        )