"""
Statistics Engine
"""

import pandas as pd

import numpy as np

from config import PRIMARY_METRICS

from utils import numeric


###########################################################################
# STATISTICS ENGINE
###########################################################################

class StatisticsEngine:

    def __init__(

        self,

        strategies

    ):

        self.strategies = strategies

    ###########################################################################
    # BUILD STRATEGY STATISTICS
    ###########################################################################

    def strategy_statistics(self):

        rows = []

        for strategy, df in self.strategies.items():

            rows.append(

                self.calculate_strategy(

                    strategy,

                    df

                )

            )

        return pd.DataFrame(

            rows

        )

    ###########################################################################
    # CALCULATE SINGLE STRATEGY
    ###########################################################################

    def calculate_strategy(

        self,

        strategy,

        dataframe

    ):

        summary = {

            "Strategy": strategy

        }

        for metric in PRIMARY_METRICS:

            if metric not in dataframe.columns:

                continue

            values = numeric(

                dataframe[metric]

            ).dropna()

            if values.empty:

                continue

            summary[f"{metric}_Mean"] = values.mean()

            summary[f"{metric}_Median"] = values.median()

            summary[f"{metric}_Min"] = values.min()

            summary[f"{metric}_Max"] = values.max()

            summary[f"{metric}_Std"] = values.std()

        summary["Total Stocks"] = len(

            dataframe

        )

        if "Recommendation" in dataframe.columns:

            recommendations = (

                dataframe["Recommendation"]

                .astype(str)

                .str.strip()

                .value_counts()

            )

            for key, value in recommendations.items():

                summary[f"{key}_Count"] = value

        return summary

    ###########################################################################
    # OVERALL SUMMARY
    ###########################################################################

    def overall_summary(self):

        df = self.strategy_statistics()

        numeric_df = df.select_dtypes(

            include=np.number

        )

        return pd.DataFrame({

            "Metric": numeric_df.columns,

            "Average": numeric_df.mean().values,

            "Maximum": numeric_df.max().values,

            "Minimum": numeric_df.min().values,

            "Std Dev": numeric_df.std().values

        })

    ###########################################################################
    # METRIC LEADERS
    ###########################################################################

    def metric_leaders(self):

        df = self.strategy_statistics()

        leaders = []

        for metric in PRIMARY_METRICS:

            column = f"{metric}_Mean"

            if column not in df.columns:

                continue

            idx = df[column].idxmax()

            leaders.append({

                "Metric": metric,

                "Strategy": df.loc[

                    idx,

                    "Strategy"

                ],

                "Value": round(

                    df.loc[

                        idx,

                        column

                    ],

                    2

                )

            })

        return pd.DataFrame(

            leaders

        )

    ###########################################################################
    # DATA QUALITY
    ###########################################################################

    def data_quality(self):

        rows = []

        for strategy, df in self.strategies.items():

            rows.append({

                "Strategy": strategy,

                "Rows": len(df),

                "Columns": len(df.columns),

                "Missing Values": int(

                    df.isna().sum().sum()

                ),

                "Duplicate Rows": int(

                    df.duplicated().sum()

                )

            })

        return pd.DataFrame(

            rows

        )