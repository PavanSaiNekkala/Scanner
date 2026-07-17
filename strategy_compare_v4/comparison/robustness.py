"""
=============================================================
Institutional Robustness Engine V4

Module:
    comparison/robustness.py

Purpose:
    Evaluate robustness and consistency of every
    strategy using institutional-quality metrics.

Outputs

    • Stability Analysis
    • Robustness Scores
    • Consistency Scores
    • Volatility Analysis
    • Outlier Detection
    • Robust Strategy Ranking

=============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class RobustnessEngine:

    """
    Institutional Robustness Engine
    """

    def __init__(

        self,

        comparison_df: pd.DataFrame

    ):

        self.df = comparison_df.copy()

        self.robustness = pd.DataFrame()

        self.consistency = pd.DataFrame()

        self.volatility = pd.DataFrame()

        self.outliers = pd.DataFrame()

        self.summary = pd.DataFrame()


    # ---------------------------------------------------------

    def validate(self):

        """
        Validate required columns.
        """

        required = [

            "Stock",

            "Strategy",

            "Composite Score",

            "Expectancy",

            "Profit Factor",

            "Reward Risk"

        ]

        missing = [

            c

            for c in required

            if c not in self.df.columns

        ]

        if missing:

            raise ValueError(

                "Missing columns:\n"

                +

                "\n".join(missing)

            )

        return self


    # ---------------------------------------------------------

    def coefficient_of_variation(self):

        """
        Calculate Coefficient of Variation
        for every strategy.
        """

        cv = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                MeanComposite=(

                    "Composite Score",

                    "mean"

                ),

                StdComposite=(

                    "Composite Score",

                    "std"

                )

            )

            .reset_index()

        )

        cv["Coefficient of Variation"] = (

            cv["StdComposite"]

            /

            cv["MeanComposite"]

        ).replace(

            [np.inf, -np.inf],

            np.nan

        ).fillna(

            0

        )

        self.robustness = cv

        return self


    # ---------------------------------------------------------

    def stability_score(self):

        """
        Higher stability
        means lower variation.
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

                *

                100

            )

        ).clip(

            lower=0,

            upper=100

        )

        return self


    # ---------------------------------------------------------

    def expectancy_stability(self):

        """
        Stability of Expectancy.
        """

        exp = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                Mean=(

                    "Expectancy",

                    "mean"

                ),

                Std=(

                    "Expectancy",

                    "std"

                )

            )

            .reset_index()

        )

        exp["Expectancy Stability"] = (

            100

            -

            (

                exp["Std"]

                /

                exp["Mean"]

            )

            .replace(

                [np.inf, -np.inf],

                np.nan

            )

            .fillna(

                0

            )

            *

            100

        ).clip(

            0,

            100

        )

        self.robustness = self.robustness.merge(

            exp[

                [

                    "Strategy",

                    "Expectancy Stability"

                ]

            ],

            on="Strategy",

            how="left"

        )

        return self


    # ---------------------------------------------------------

    def profit_factor_stability(self):

        """
        Stability of Profit Factor.
        """

        pf = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                Mean=(

                    "Profit Factor",

                    "mean"

                ),

                Std=(

                    "Profit Factor",

                    "std"

                )

            )

            .reset_index()

        )

        pf["Profit Stability"] = (

            100

            -

            (

                pf["Std"]

                /

                pf["Mean"]

            )

            .replace(

                [np.inf, -np.inf],

                np.nan

            )

            .fillna(

                0

            )

            *

            100

        ).clip(

            0,

            100

        )

        self.robustness = self.robustness.merge(

            pf[

                [

                    "Strategy",

                    "Profit Stability"

                ]

            ],

            on="Strategy",

            how="left"

        )

        return self


    # ---------------------------------------------------------

    def reward_risk_stability(self):

        """
        Stability of Reward Risk.
        """

        rr = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                Mean=(

                    "Reward Risk",

                    "mean"

                ),

                Std=(

                    "Reward Risk",

                    "std"

                )

            )

            .reset_index()

        )

        rr["RewardRisk Stability"] = (

            100

            -

            (

                rr["Std"]

                /

                rr["Mean"]

            )

            .replace(

                [np.inf, -np.inf],

                np.nan

            )

            .fillna(

                0

            )

            *

            100

        ).clip(

            0,

            100

        )

        self.robustness = self.robustness.merge(

            rr[

                [

                    "Strategy",

                    "RewardRisk Stability"

                ]

            ],

            on="Strategy",

            how="left"

        )

        return self


    # ---------------------------------------------------------

    def composite_consistency(self):

        """
        Composite consistency
        across stocks.
        """

        consistency = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                Average=(

                    "Composite Score",

                    "mean"

                ),

                Median=(

                    "Composite Score",

                    "median"

                ),

                Std=(

                    "Composite Score",

                    "std"

                )

            )

            .reset_index()

        )

        consistency["Consistency Score"] = (

            100

            -

            consistency["Std"]

        ).clip(

            0,

            100

        )

        self.consistency = consistency

        return self

    # ---------------------------------------------------------

    def volatility_analysis(self):

        """
        Volatility analysis for
        every strategy.
        """

        self.volatility = (

            self.df

            .groupby(

                "Strategy"

            )

            .agg(

                CompositeStd=(

                    "Composite Score",

                    "std"

                ),

                ExpectancyStd=(

                    "Expectancy",

                    "std"

                ),

                ProfitFactorStd=(

                    "Profit Factor",

                    "std"

                ),

                RewardRiskStd=(

                    "Reward Risk",

                    "std"

                )

            )

            .reset_index()

        )

        self.volatility["Volatility Score"] = (

            100

            -

            self.volatility[

                "CompositeStd"

            ]

        ).clip(

            0,

            100

        )

        return self


    # ---------------------------------------------------------

    def detect_outliers(self):

        """
        Detect outliers using Z-score.
        """

        temp = self.df.copy()

        temp["ZScore"] = (

            temp["Composite Score"]

            -

            temp["Composite Score"].mean()

        ) / (

            temp["Composite Score"].std()

        )

        self.outliers = (

            temp

            .loc[

                temp["ZScore"].abs() > 3

            ]

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def robustness_score(self):

        """
        Final institutional
        robustness score.
        """

        self.robustness = (

            self.robustness

            .merge(

                self.consistency[

                    [

                        "Strategy",

                        "Consistency Score"

                    ]

                ],

                on="Strategy",

                how="left"

            )

            .merge(

                self.volatility[

                    [

                        "Strategy",

                        "Volatility Score"

                    ]

                ],

                on="Strategy",

                how="left"

            )

        )

        self.robustness["Robustness Score"] = (

            self.robustness[

                [

                    "Stability Score",

                    "Expectancy Stability",

                    "Profit Stability",

                    "RewardRisk Stability",

                    "Consistency Score",

                    "Volatility Score"

                ]

            ]

            .mean(

                axis=1

            )

            .round(

                2

            )

        )

        return self


    # ---------------------------------------------------------

    def rank_strategies(self):

        """
        Rank strategies by
        robustness.
        """

        self.robustness = (

            self.robustness

            .sort_values(

                "Robustness Score",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.robustness.insert(

            0,

            "Robustness Rank",

            np.arange(

                1,

                len(

                    self.robustness

                ) + 1

            )

        )

        return self


    # ---------------------------------------------------------

    def summary_report(self):

        """
        Executive summary.
        """

        self.summary = pd.DataFrame(

            {

                "Metric":[

                    "Strategies",

                    "Stocks",

                    "Average Robustness",

                    "Maximum Robustness",

                    "Minimum Robustness",

                    "Outliers"

                ],

                "Value":[

                    self.df["Strategy"].nunique(),

                    self.df["Stock"].nunique(),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].mean(),

                        2

                    ),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].max(),

                        2

                    ),

                    round(

                        self.robustness[

                            "Robustness Score"

                        ].min(),

                        2

                    ),

                    len(

                        self.outliers

                    )

                ]

            }

        )

        return self


    # ---------------------------------------------------------

    def diagnostics(self):

        """
        Console diagnostics.
        """

        print()

        print("=" * 70)

        print("INSTITUTIONAL ROBUSTNESS ENGINE")

        print("=" * 70)

        print(

            f"Strategies : {self.df['Strategy'].nunique()}"

        )

        print(

            f"Stocks     : {self.df['Stock'].nunique()}"

        )

        print(

            f"Average Robustness : "

            f"{self.robustness['Robustness Score'].mean():.2f}"

        )

        print(

            f"Maximum Robustness : "

            f"{self.robustness['Robustness Score'].max():.2f}"

        )

        print(

            f"Outliers : {len(self.outliers)}"

        )

        print("=" * 70)

        print()

        return self


    # ---------------------------------------------------------

    def export(

        self,

        output="Institutional_Robustness.xlsx"

    ):

        """
        Export workbook.
        """

        with pd.ExcelWriter(

            output,

            engine="openpyxl"

        ) as writer:

            self.robustness.to_excel(

                writer,

                sheet_name="Robustness",

                index=False

            )

            self.consistency.to_excel(

                writer,

                sheet_name="Consistency",

                index=False

            )

            self.volatility.to_excel(

                writer,

                sheet_name="Volatility",

                index=False

            )

            self.outliers.to_excel(

                writer,

                sheet_name="Outliers",

                index=False

            )

            self.summary.to_excel(

                writer,

                sheet_name="Summary",

                index=False

            )

        return self


    # ---------------------------------------------------------

    def get_results(self):

        """
        Return generated reports.
        """

        return {

            "robustness": self.robustness,

            "consistency": self.consistency,

            "volatility": self.volatility,

            "outliers": self.outliers,

            "summary": self.summary

        }


    # ---------------------------------------------------------

    def run(self):

        """
        Execute complete robustness pipeline.
        """

        return (

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


# ==========================================================
# Convenience Function
# ==========================================================

def analyze_robustness(

    comparison_df,

    output_file="Institutional_Robustness.xlsx"

):

    engine = (

        RobustnessEngine(

            comparison_df

        )

        .run()

    )

    engine.export(

        output_file

    )

    return engine


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    print(

        "Import analyze_robustness() from strategy_compare.py"

    )