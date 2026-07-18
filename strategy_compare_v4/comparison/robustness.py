"""
=============================================================
Institutional Robustness Engine V4

Module
------
comparison/robustness.py

Purpose
-------
Evaluate robustness and consistency of every
strategy using institutional-quality metrics.

Outputs
-------
• Stability Analysis
• Robustness Scores
• Consistency Scores
• Volatility Analysis
• Outlier Detection
• Robust Strategy Ranking

=============================================================
"""

from __future__ import annotations

import time
from typing import Dict

import numpy as np
import pandas as pd

from strategy_compare_v4.config.constants import (
    REQUIRED_COMPARISON_COLUMNS,
    COMPOSITE_SCORE,
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
# Robustness Engine
# ============================================================

class RobustnessEngine:
    """
    Institutional Robustness Engine.

    Responsibilities
    ----------------
    • Evaluate strategy robustness
    • Measure statistical stability
    • Calculate consistency metrics
    • Perform volatility analysis
    • Detect outliers
    • Rank strategies by robustness
    """

    def __init__(
        self,
        comparison_df: pd.DataFrame,
    ):

        self.df = comparison_df.copy()

        self.robustness = pd.DataFrame()

        self.consistency = pd.DataFrame()

        self.volatility = pd.DataFrame()

        self.outliers = pd.DataFrame()

        self.summary = pd.DataFrame()

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

            "Validating Robustness Input",

        )

        require_columns(

            self.df,

            REQUIRED_COMPARISON_COLUMNS,

        )

        logger.info(

            "Validation successful."

        )

        logger.info(

            "Rows       : %d",

            len(self.df),

        )

        logger.info(

            "Stocks     : %d",

            self.df["Stock"].nunique(),

        )

        logger.info(

            "Strategies : %d",

            self.df["Strategy"].nunique(),

        )

        logger.info(

            "Average Composite : %.2f",

            self.df[COMPOSITE_SCORE].mean(),

        )

        return self
    
    # ---------------------------------------------------------
    # Coefficient of Variation
    # ---------------------------------------------------------

    def coefficient_of_variation(self):

        """
        Calculate the Coefficient of Variation
        for every strategy.
        """

        self.robustness = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                MeanComposite=(

                    COMPOSITE_SCORE,

                    "mean",

                ),

                StdComposite=(

                    COMPOSITE_SCORE,

                    "std",

                ),

            )

        )

        self.robustness["Coefficient of Variation"] = safe_divide(

            self.robustness["StdComposite"],

            self.robustness["MeanComposite"],

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Coefficient of Variation calculated."

        )

        return self

    # ---------------------------------------------------------
    # Stability Score
    # ---------------------------------------------------------

    def stability_score(self):

        """
        Calculate Stability Score.

        Higher stability implies
        lower variation.
        """

        self.robustness[

            "Stability Score"

        ] = (

            100

            -

            (

                self.robustness[

                    "Coefficient of Variation"

                ]

                * 100

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Stability scores calculated."

        )

        return self

    # ---------------------------------------------------------
    # Expectancy Stability
    # ---------------------------------------------------------

    def expectancy_stability(self):

        """
        Calculate Expectancy Stability.
        """

        expectancy = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                Mean=(

                    "Expectancy",

                    "mean",

                ),

                Std=(

                    "Expectancy",

                    "std",

                ),

            )

        )

        expectancy["Expectancy Stability"] = (

            100

            -

            (

                safe_divide(

                    expectancy["Std"],

                    expectancy["Mean"],

                )

                * 100

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.robustness = (

            self.robustness

            .merge(

                expectancy[

                    [

                        "Strategy",

                        "Expectancy Stability",

                    ]

                ],

                on="Strategy",

                how="left",

            )

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Expectancy stability calculated."

        )

        return self

    # ---------------------------------------------------------
    # Profit Factor Stability
    # ---------------------------------------------------------

    def profit_factor_stability(self):

        """
        Calculate Profit Factor Stability.
        """

        profit = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                Mean=(

                    "Profit Factor",

                    "mean",

                ),

                Std=(

                    "Profit Factor",

                    "std",

                ),

            )

        )

        profit["Profit Stability"] = (

            100

            -

            (

                safe_divide(

                    profit["Std"],

                    profit["Mean"],

                )

                * 100

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.robustness = (

            self.robustness

            .merge(

                profit[

                    [

                        "Strategy",

                        "Profit Stability",

                    ]

                ],

                on="Strategy",

                how="left",

            )

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Profit Factor stability calculated."

        )

        return self

    # ---------------------------------------------------------
    # Reward Risk Stability
    # ---------------------------------------------------------

    def reward_risk_stability(self):

        """
        Calculate Reward Risk Stability.
        """

        reward = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                Mean=(

                    "Reward Risk",

                    "mean",

                ),

                Std=(

                    "Reward Risk",

                    "std",

                ),

            )

        )

        reward["RewardRisk Stability"] = (

            100

            -

            (

                safe_divide(

                    reward["Std"],

                    reward["Mean"],

                )

                * 100

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.robustness = (

            self.robustness

            .merge(

                reward[

                    [

                        "Strategy",

                        "RewardRisk Stability",

                    ]

                ],

                on="Strategy",

                how="left",

            )

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Reward Risk stability calculated."

        )

        return self
    
    # ---------------------------------------------------------
    # Composite Consistency
    # ---------------------------------------------------------

    def composite_consistency(self):

        """
        Calculate Composite Score
        consistency across stocks.
        """

        self.consistency = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                Average=(

                    COMPOSITE_SCORE,

                    "mean",

                ),

                Median=(

                    COMPOSITE_SCORE,

                    "median",

                ),

                Std=(

                    COMPOSITE_SCORE,

                    "std",

                ),

            )

        )

        self.consistency[

            "Consistency Score"

        ] = (

            100

            -

            self.consistency[

                "Std"

            ].fillna(

                0

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.consistency = round_dataframe(

            self.consistency,

            decimals=2,

        )

        logger.info(

            "Composite consistency calculated."

        )

        return self

    # ---------------------------------------------------------
    # Volatility Analysis
    # ---------------------------------------------------------

    def volatility_analysis(self):

        """
        Calculate volatility metrics
        for every strategy.
        """

        self.volatility = (

            self.df

            .groupby(

                "Strategy",

                as_index=False,

            )

            .agg(

                CompositeStd=(

                    COMPOSITE_SCORE,

                    "std",

                ),

                ExpectancyStd=(

                    "Expectancy",

                    "std",

                ),

                ProfitFactorStd=(

                    "Profit Factor",

                    "std",

                ),

                RewardRiskStd=(

                    "Reward Risk",

                    "std",

                ),

            )

        )

        self.volatility[

            "Volatility Score"

        ] = (

            100

            -

            self.volatility[

                "CompositeStd"

            ].fillna(

                0

            )

        ).clip(

            lower=0,

            upper=100,

        )

        self.volatility = round_dataframe(

            self.volatility,

            decimals=2,

        )

        logger.info(

            "Volatility analysis completed."

        )

        return self

    # ---------------------------------------------------------
    # Detect Outliers
    # ---------------------------------------------------------

    def detect_outliers(self):

        """
        Detect Composite Score
        outliers using Z-score.
        """

        temp = self.df.copy()

        std = temp[

            COMPOSITE_SCORE

        ].std()

        if std == 0 or pd.isna(std):

            temp["ZScore"] = 0

        else:

            temp["ZScore"] = (

                temp[

                    COMPOSITE_SCORE

                ]

                -

                temp[

                    COMPOSITE_SCORE

                ].mean()

            ) / std

        self.outliers = (

            temp

            .loc[

                temp["ZScore"].abs() > 3

            ]

            .reset_index(

                drop=True,

            )

        )

        self.outliers = round_dataframe(

            self.outliers,

            decimals=2,

        )

        logger.info(

            "Detected %d outliers.",

            len(

                self.outliers

            ),

        )

        return self

    # ---------------------------------------------------------
    # Robustness Score
    # ---------------------------------------------------------

    def robustness_score(self):

        """
        Calculate final institutional
        robustness score.
        """

        self.robustness = (

            self.robustness

            .merge(

                self.consistency[

                    [

                        "Strategy",

                        "Consistency Score",

                    ]

                ],

                on="Strategy",

                how="left",

            )

            .merge(

                self.volatility[

                    [

                        "Strategy",

                        "Volatility Score",

                    ]

                ],

                on="Strategy",

                how="left",

            )

        )

        score_columns = [

            "Stability Score",

            "Expectancy Stability",

            "Profit Stability",

            "RewardRisk Stability",

            "Consistency Score",

            "Volatility Score",

        ]

        self.robustness[

            "Robustness Score"

        ] = (

            self.robustness[

                score_columns

            ]

            .mean(

                axis=1,

            )

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Robustness scores calculated."

        )

        return self

    # ---------------------------------------------------------
    # Rank Strategies
    # ---------------------------------------------------------

    def rank_strategies(self):

        """
        Rank strategies using
        robustness score.
        """

        self.robustness = (

            self.robustness

            .sort_values(

                "Robustness Score",

                ascending=False,

            )

            .reset_index(

                drop=True,

            )

        )

        self.robustness.insert(

            0,

            "Robustness Rank",

            np.arange(

                1,

                len(

                    self.robustness

                ) + 1,

            ),

        )

        self.robustness = round_dataframe(

            self.robustness,

            decimals=2,

        )

        logger.info(

            "Strategies ranked by robustness."

        )

        return self
    
    # ---------------------------------------------------------
    # Summary Report
    # ---------------------------------------------------------

    def summary_report(self):

        """
        Generate executive summary.
        """

        self.summary = pd.DataFrame(

            {

                "Metric": [

                    "Strategies",

                    "Stocks",

                    "Average Robustness",

                    "Maximum Robustness",

                    "Minimum Robustness",

                    "Outliers",

                ],

                "Value": [

                    self.df[

                        "Strategy"

                    ].nunique(),

                    self.df[

                        "Stock"

                    ].nunique(),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].mean(),

                        2,

                    ),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].max(),

                        2,

                    ),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].min(),

                        2,

                    ),

                    len(

                        self.outliers,

                    ),

                ],

            }

        )

        logger.info(

            "Executive summary generated."

        )

        return self

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    def diagnostics(self):

        """
        Generate execution diagnostics.
        """

        self.diagnostic_report = {

            "Strategies":

                self.df[

                    "Strategy"

                ].nunique(),

            "Stocks":

                self.df[

                    "Stock"

                ].nunique(),

            "Average Robustness":

                round(

                    self.robustness[

                        "Robustness Score"

                    ].mean(),

                    2,

                ),

            "Maximum Robustness":

                round(

                    self.robustness[

                        "Robustness Score"

                    ].max(),

                    2,

                ),

            "Minimum Robustness":

                round(

                    self.robustness[

                        "Robustness Score"

                    ].min(),

                    2,

                ),

            "Outliers":

                len(

                    self.outliers,

                ),

        }

        logger.info(

            "Diagnostics generated."

        )

        return self

    # ---------------------------------------------------------
    # Execution Report
    # ---------------------------------------------------------

    def execution_report(self):

        """
        Log execution summary.
        """

        banner(

            logger,

            "Institutional Robustness Completed",

        )

        for key, value in self.diagnostic_report.items():

            logger.info(

                "%-30s : %s",

                key,

                value,

            )

        logger.info(

            "Execution Time (s)           : %.3f",

            self.execution_time,

        )

        return self

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export(

        self,

        output_file: str = "Institutional_Robustness.xlsx",

    ):

        """
        Export all generated reports.
        """

        from strategy_compare_v4.utils.io_utils import (

            write_excel,

        )

        sheets = {

            "Robustness":

                self.robustness,

            "Consistency":

                self.consistency,

            "Volatility":

                self.volatility,

            "Outliers":

                self.outliers,

            "Summary":

                self.summary,

        }

        write_excel(

            sheets,

            output_file,

        )

        logger.info(

            "Robustness workbook exported -> %s",

            output_file,

        )

        return self

    # ---------------------------------------------------------
    # Get Results
    # ---------------------------------------------------------

    def get_results(self):

        """
        Return generated reports.
        """

        return {

            "robustness":

                self.robustness,

            "consistency":

                self.consistency,

            "volatility":

                self.volatility,

            "outliers":

                self.outliers,

            "summary":

                self.summary,

        }

    # ---------------------------------------------------------
    # Execute Pipeline
    # ---------------------------------------------------------

    def run(self):

        """
        Execute complete robustness pipeline.
        """

        start = time.perf_counter()

        try:

            (

                self

                .validate()

                .coefficient_of_variation()

                .stability_score()

                .expectancy_stability()

                .profit_factor_stability()

                .reward_risk_stability()

                .composite_consistency()

                .volatility_analysis()

                .detect_outliers()

                .robustness_score()

                .rank_strategies()

                .summary_report()

                .diagnostics()

            )

        except Exception as exc:

            logger.exception(

                "Robustness Engine failed."

            )

            raise RuntimeError(

                f"Robustness Engine failed:\n{exc}"

            ) from exc

        finally:

            self.execution_time = round(

                time.perf_counter()

                - start,

                3,

            )

        self.execution_report()

        return self


# ============================================================
# Convenience Function
# ============================================================

def analyze_robustness(

    comparison_df: pd.DataFrame,

    output_file: str = "Institutional_Robustness.xlsx",

) -> RobustnessEngine:

    """
    Execute the institutional
    robustness engine.
    """

    engine = (

        RobustnessEngine(

            comparison_df,

        )

        .run()

    )

    engine.export(

        output_file,

    )

    return engine


# ============================================================
# Main
# ============================================================

def main():

    import argparse

    parser = argparse.ArgumentParser(

        description=(

            "Institutional "

            "Robustness Engine V4"

        )

    )

    parser.add_argument(

        "--input",

        required=True,

        help="Comparison workbook",

    )

    parser.add_argument(

        "--output",

        default="Institutional_Robustness.xlsx",

        help="Output workbook",

    )

    args = parser.parse_args()

    from strategy_compare_v4.utils.io_utils import (

        read_excel,

    )

    comparison_df = read_excel(

        args.input,

    )

    analyze_robustness(

        comparison_df,

        args.output,

    )


if __name__ == "__main__":

    main()