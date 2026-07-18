"""
=============================================================
Institutional Correlation Engine V4

Module
------
comparison/correlation.py

Purpose
-------
Analyze similarity and diversification between
strategies using institutional-level correlation
analysis.

Outputs
-------
• Pearson Correlation
• Spearman Correlation
• Kendall Correlation
• Strategy Similarity
• Stock Similarity
• Diversification Score
• Correlation Ranking

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
    round_dataframe,
)

from strategy_compare_v4.utils.logger import (
    get_logger,
    banner,
)

logger = get_logger(__name__)


# ============================================================
# Correlation Engine
# ============================================================

class CorrelationEngine:
    """
    Institutional Correlation Engine.

    Responsibilities
    ----------------
    • Analyze strategy similarity
    • Compute correlation matrices
    • Measure diversification
    • Detect highly correlated strategies
    • Produce institutional reports
    """

    def __init__(
        self,
        comparison_df: pd.DataFrame,
    ):

        self.df = comparison_df.copy()

        self.strategy_matrix = pd.DataFrame()

        self.stock_matrix = pd.DataFrame()

        self.pearson = pd.DataFrame()

        self.spearman = pd.DataFrame()

        self.kendall = pd.DataFrame()

        self.diversification = pd.DataFrame()

        self.correlation_pairs = pd.DataFrame()

        self.cluster_report = pd.DataFrame()

        self.heatmap = pd.DataFrame()

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

            "Validating Correlation Input",

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
    # Strategy Matrix
    # ---------------------------------------------------------

    def create_strategy_matrix(self):

        """
        Create Strategy vs Stock matrix.
        """

        self.strategy_matrix = (

            self.df

            .pivot_table(

                index="Stock",

                columns="Strategy",

                values=COMPOSITE_SCORE,

                aggfunc="mean",

            )

            .sort_index()

            .sort_index(

                axis=1,

            )

        )

        self.strategy_matrix = round_dataframe(

            self.strategy_matrix,

            decimals=4,

        )

        logger.info(

            "Strategy matrix created (%d × %d).",

            self.strategy_matrix.shape[0],

            self.strategy_matrix.shape[1],

        )

        return self

    # ---------------------------------------------------------
    # Stock Matrix
    # ---------------------------------------------------------

    def create_stock_matrix(self):

        """
        Create Stock similarity matrix.
        """

        self.stock_matrix = (

            self.df

            .pivot_table(

                index="Strategy",

                columns="Stock",

                values=COMPOSITE_SCORE,

                aggfunc="mean",

            )

            .sort_index()

            .sort_index(

                axis=1,

            )

        )

        self.stock_matrix = round_dataframe(

            self.stock_matrix,

            decimals=4,

        )

        logger.info(

            "Stock matrix created (%d × %d).",

            self.stock_matrix.shape[0],

            self.stock_matrix.shape[1],

        )

        return self

    # ---------------------------------------------------------
    # Pearson Correlation
    # ---------------------------------------------------------

    def pearson_correlation(self):

        """
        Calculate Pearson correlation
        between strategies.
        """

        self.pearson = (

            self.strategy_matrix

            .corr(

                method="pearson",

            )

        )

        self.pearson = round_dataframe(

            self.pearson,

            decimals=4,

        )

        logger.info(

            "Pearson correlation calculated."

        )

        return self

    # ---------------------------------------------------------
    # Spearman Correlation
    # ---------------------------------------------------------

    def spearman_correlation(self):

        """
        Calculate Spearman correlation
        between strategies.
        """

        self.spearman = (

            self.strategy_matrix

            .corr(

                method="spearman",

            )

        )

        self.spearman = round_dataframe(

            self.spearman,

            decimals=4,

        )

        logger.info(

            "Spearman correlation calculated."

        )

        return self

    # ---------------------------------------------------------
    # Kendall Correlation
    # ---------------------------------------------------------

    def kendall_correlation(self):

        """
        Calculate Kendall correlation
        between strategies.
        """

        self.kendall = (

            self.strategy_matrix

            .corr(

                method="kendall",

            )

        )

        self.kendall = round_dataframe(

            self.kendall,

            decimals=4,

        )

        logger.info(

            "Kendall correlation calculated."

        )

        return self
    
    # ---------------------------------------------------------
    # Diversification Score
    # ---------------------------------------------------------

    def diversification_score(self):

        """
        Calculate institutional diversification
        score from the Pearson correlation matrix.
        """

        corr = self.pearson.copy()

        np.fill_diagonal(

            corr.values,

            np.nan,

        )

        score = (

            1

            -

            corr.abs().mean()

        ) * 100

        self.diversification = pd.DataFrame(

            {

                "Strategy":

                    score.index,

                "Diversification Score":

                    score.values,

            }

        )

        self.diversification = round_dataframe(

            self.diversification,

            decimals=2,

        )

        logger.info(

            "Diversification scores calculated."

        )

        return self

    # ---------------------------------------------------------
    # Similarity Ranking
    # ---------------------------------------------------------

    def similarity_rank(self):

        """
        Rank strategies based on
        diversification score.
        """

        self.diversification = (

            self.diversification

            .sort_values(

                "Diversification Score",

                ascending=False,

            )

            .reset_index(

                drop=True,

            )

        )

        self.diversification.insert(

            0,

            "Rank",

            np.arange(

                1,

                len(

                    self.diversification,

                ) + 1,

            ),

        )

        self.diversification = round_dataframe(

            self.diversification,

            decimals=2,

        )

        logger.info(

            "Diversification ranking generated."

        )

        return self

    # ---------------------------------------------------------
    # Executive Summary
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

                    "Average Diversification",

                    "Maximum Diversification",

                    "Minimum Diversification",

                ],

                "Value": [

                    self.df[

                        "Strategy"

                    ].nunique(),

                    self.df[

                        "Stock"

                    ].nunique(),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].mean(),

                        2,

                    ),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].max(),

                        2,

                    ),

                    round(

                        self.diversification[

                            "Diversification Score"

                        ].min(),

                        2,

                    ),

                ],

            }

        )

        logger.info(

            "Executive summary generated."

        )

        return self

    # ---------------------------------------------------------
    # Classify Correlations
    # ---------------------------------------------------------

    def classify_correlations(self):

        """
        Classify pairwise strategy
        correlations.
        """

        rows = []

        for strategy_a in self.pearson.index:

            for strategy_b in self.pearson.columns:

                if strategy_a >= strategy_b:

                    continue

                correlation = self.pearson.loc[

                    strategy_a,

                    strategy_b,

                ]

                if pd.isna(

                    correlation,

                ):

                    continue

                absolute = abs(

                    correlation,

                )

                if absolute >= 0.90:

                    strength = "Very High"

                elif absolute >= 0.75:

                    strength = "High"

                elif absolute >= 0.50:

                    strength = "Moderate"

                elif absolute >= 0.25:

                    strength = "Low"

                else:

                    strength = "Very Low"

                rows.append(

                    {

                        "Strategy A":

                            strategy_a,

                        "Strategy B":

                            strategy_b,

                        "Correlation":

                            correlation,

                        "Strength":

                            strength,

                    }

                )

        self.correlation_pairs = pd.DataFrame(

            rows,

        )

        if not self.correlation_pairs.empty:

            self.correlation_pairs = (

                self.correlation_pairs

                .sort_values(

                    "Correlation",

                    ascending=False,

                )

                .reset_index(

                    drop=True,

                )

            )

            self.correlation_pairs = round_dataframe(

                self.correlation_pairs,

                decimals=4,

            )

        logger.info(

            "Correlation pairs classified."

        )

        return self

    # ---------------------------------------------------------
    # Detect Clusters
    # ---------------------------------------------------------

    def detect_clusters(self):

        """
        Detect highly correlated
        strategy clusters.
        """

        if self.correlation_pairs.empty:

            self.cluster_report = pd.DataFrame()

        else:

            self.cluster_report = (

                self.correlation_pairs

                .loc[

                    self.correlation_pairs[

                        "Correlation"

                    ].abs()

                    >= 0.80

                ]

                .reset_index(

                    drop=True,

                )

            )

        logger.info(

            "Detected %d highly correlated pairs.",

            len(

                self.cluster_report,

            ),

        )

        return self

    # ---------------------------------------------------------
    # Heatmap Matrix
    # ---------------------------------------------------------

    def heatmap_matrix(self):

        """
        Generate rounded heatmap
        correlation matrix.
        """

        self.heatmap = round_dataframe(

            self.pearson.copy(),

            decimals=3,

        )

        logger.info(

            "Heatmap matrix generated."

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

            "Average Diversification":

                round(

                    self.diversification[

                        "Diversification Score"

                    ].mean(),

                    2,

                ),

            "Maximum Diversification":

                round(

                    self.diversification[

                        "Diversification Score"

                    ].max(),

                    2,

                ),

            "Minimum Diversification":

                round(

                    self.diversification[

                        "Diversification Score"

                    ].min(),

                    2,

                ),

            "Highly Correlated Pairs":

                len(

                    self.cluster_report,

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

            "Institutional Correlation Completed",

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

        output_file: str = "Institutional_Correlation.xlsx",

    ):

        """
        Export all generated reports.
        """

        from strategy_compare_v4.utils.io_utils import (

            write_excel,

        )

        sheets = {

            "Pearson":

                self.pearson,

            "Spearman":

                self.spearman,

            "Kendall":

                self.kendall,

            "Heatmap":

                self.heatmap,

            "Diversification":

                self.diversification,

            "Correlation Pairs":

                self.correlation_pairs,

            "Clusters":

                self.cluster_report,

            "Summary":

                self.summary,

        }

        write_excel(

            sheets,

            output_file,

        )

        logger.info(

            "Correlation workbook exported -> %s",

            output_file,

        )

        return self

    # ---------------------------------------------------------
    # Get Results
    # ---------------------------------------------------------

    def get_results(self):

        """
        Return all generated reports.
        """

        return {

            "pearson":

                self.pearson,

            "spearman":

                self.spearman,

            "kendall":

                self.kendall,

            "heatmap":

                self.heatmap,

            "diversification":

                self.diversification,

            "pairs":

                self.correlation_pairs,

            "clusters":

                self.cluster_report,

            "summary":

                self.summary,

        }

    # ---------------------------------------------------------
    # Execute Pipeline
    # ---------------------------------------------------------

    def run(self):

        """
        Execute the complete
        correlation pipeline.
        """

        start = time.perf_counter()

        try:

            (

                self

                .validate()

                .create_strategy_matrix()

                .create_stock_matrix()

                .pearson_correlation()

                .spearman_correlation()

                .kendall_correlation()

                .diversification_score()

                .similarity_rank()

                .summary_report()

                .classify_correlations()

                .detect_clusters()

                .heatmap_matrix()

                .diagnostics()

            )

        except Exception as exc:

            logger.exception(

                "Correlation Engine failed."

            )

            raise RuntimeError(

                f"Correlation Engine failed:\n{exc}"

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

def analyze_correlations(

    comparison_df: pd.DataFrame,

    output_file: str = "Institutional_Correlation.xlsx",

) -> CorrelationEngine:

    """
    Execute the institutional
    correlation engine.
    """

    engine = (

        CorrelationEngine(

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

            "Correlation Engine V4"

        )

    )

    parser.add_argument(

        "--input",

        required=True,

        help="Comparison workbook",

    )

    parser.add_argument(

        "--output",

        default="Institutional_Correlation.xlsx",

        help="Output workbook",

    )

    args = parser.parse_args()

    from strategy_compare_v4.utils.io_utils import (

        read_excel,

    )

    comparison_df = read_excel(

        args.input,

    )

    analyze_correlations(

        comparison_df,

        args.output,

    )


if __name__ == "__main__":

    main()