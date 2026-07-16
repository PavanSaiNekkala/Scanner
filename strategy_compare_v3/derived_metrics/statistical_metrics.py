"""
============================================================
Institutional Strategy Comparison Engine V3

File : derived_metrics/statistical_metrics.py

Statistical Metrics Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.logger import get_logger


logger = get_logger(__name__)


class StatisticalMetricsEngine:
    """
    Generates statistical distribution metrics
    for all numerical backtest trade fields.


    Input
    -----

    Any numerical trade columns.

    Examples:

    gross_return_Pct
    net_return_Pct
    days_held
    entry_price
    exit_price
    target_price
    stop_price
    rsi14
    atr_pct
    roc10


    Generated Metrics
    -----------------

    Sum
    Mean
    Median
    Minimum
    Maximum
    Range
    Variance
    Standard Deviation
    Coefficient of Variation
    Skewness
    Kurtosis
    Percentiles

    """



    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.copy()



    # ==================================================
    # BASIC STATISTICS
    # ==================================================

    def generate_basic_statistics(self):

        numeric_columns = (

            self.df

            .select_dtypes(

                include=np.number

            )

            .columns

        )


        statistics = []



        for column in numeric_columns:


            series = (

                self.df[column]

                .dropna()

            )


            if series.empty:

                continue



            statistics.append({

                "Feature":

                    column,


                "Count":

                    series.count(),


                "Sum":

                    series.sum(),


                "Mean":

                    series.mean(),


                "Median":

                    series.median(),


                "Min":

                    series.min(),


                "Max":

                    series.max(),


                "Range":

                    series.max()

                    -

                    series.min(),


                "Variance":

                    series.var(),


                "Std Dev":

                    series.std(),


                "Skewness":

                    series.skew(),


                "Kurtosis":

                    series.kurtosis(),

            })



        return pd.DataFrame(statistics)



    # ==================================================
    # COEFFICIENT OF VARIATION
    # ==================================================

    def coefficient_variation(
        self,
        statistics_df
    ):


        statistics_df["Coefficient Variation"] = (

            statistics_df["Std Dev"]

            /

            statistics_df["Mean"].replace(

                0,

                np.nan

            )

        )


        return statistics_df



    # ==================================================
    # PERCENTILE ANALYSIS
    # ==================================================

    def percentile_analysis(self):


        numeric_columns = (

            self.df

            .select_dtypes(

                include=np.number

            )

            .columns

        )


        percentile_data = []



        for column in numeric_columns:


            series = (

                self.df[column]

                .dropna()

            )


            if series.empty:

                continue



            percentile_data.append({

                "Feature":

                    column,


                "P10":

                    series.quantile(0.10),


                "P25":

                    series.quantile(0.25),


                "P50":

                    series.quantile(0.50),


                "P75":

                    series.quantile(0.75),


                "P90":

                    series.quantile(0.90),


                "P95":

                    series.quantile(0.95)

            })


        return pd.DataFrame(percentile_data)



    # ==================================================
    # TRADE DISTRIBUTION QUALITY
    # ==================================================

    def trade_distribution_quality(
        self
    ):


        if "net_return_Pct" not in self.df.columns:

            return pd.DataFrame()



        returns = (

            self.df["net_return_Pct"]

            .dropna()

        )


        result = {


            "Winning Trades":

                (

                    returns > 0

                ).sum(),


            "Losing Trades":

                (

                    returns < 0

                ).sum(),


            "Win Rate":

                (

                    (returns > 0).mean()

                    *

                    100

                ),


            "Average Return":

                returns.mean(),


            "Best Trade":

                returns.max(),


            "Worst Trade":

                returns.min(),


            "Return Volatility":

                returns.std(),


        }


        return pd.DataFrame(

            [result]

        )



    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):


        logger.info(

            "Generating Statistical Metrics..."

        )



        statistics = (

            self.generate_basic_statistics()

        )


        statistics = (

            self.coefficient_variation(

                statistics

            )

        )


        percentiles = (

            self.percentile_analysis()

        )


        distribution = (

            self.trade_distribution_quality()

        )


        logger.info(

            "Statistical Metrics completed."

        )


        return {


            "Statistics":

                statistics,


            "Percentiles":

                percentiles,


            "Trade Distribution":

                distribution

        }



if __name__ == "__main__":

    print(

        "Import StatisticalMetricsEngine"

    )