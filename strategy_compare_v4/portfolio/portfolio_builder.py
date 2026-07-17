"""
=============================================================
Institutional Portfolio Builder V4

Module:
    portfolio/portfolio_builder.py

Purpose:
    Construct an institutional-grade portfolio using
    the outputs from the Strategy Comparison Engine.

Features

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

import numpy as np
import pandas as pd


class PortfolioBuilder:

    """
    Institutional Portfolio Builder
    """

    def __init__(

        self,

        comparison_df: pd.DataFrame

    ):

        self.df = comparison_df.copy()

        self.filtered = pd.DataFrame()

        self.portfolio = pd.DataFrame()

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

            "Recommendation"

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

    def recommendation_filter(

        self,

        recommendations=(

            "Strong Buy",

            "Buy",

            "Watch"

        )

    ):

        """
        Keep only desired recommendations.
        """

        self.filtered = (

            self.df

            .loc[

                self.df[

                    "Recommendation"

                ]

                .isin(

                    recommendations

                )

            ]

            .copy()

        )

        return self


    # ---------------------------------------------------------

    def top_n(

        self,

        n=25

    ):

        """
        Select Top-N opportunities.
        """

        self.filtered = (

            self.filtered

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .head(

                n

            )

            .reset_index(

                drop=True

            )

        )

        return self


    # ---------------------------------------------------------

    def equal_weight_portfolio(self):

        """
        Equal weighted allocation.
        """

        self.portfolio = (

            self.filtered.copy()

        )

        weight = (

            100

            /

            len(

                self.portfolio

            )

        )

        self.portfolio[

            "Weight %"

        ] = round(

            weight,

            2

        )

        return self


    # ---------------------------------------------------------

    def score_weight_portfolio(self):

        """
        Composite Score weighted allocation.
        """

        total = (

            self.portfolio[

                "Composite Score"

            ]

            .sum()

        )

        self.portfolio[

            "Score Weight %"

        ] = (

            self.portfolio[

                "Composite Score"

            ]

            /

            total

            *

            100

        ).round(

            2

        )

        return self


    # ---------------------------------------------------------

    def allocation_amount(

        self,

        capital=100000

    ):

        """
        Allocate capital.
        """

        self.portfolio[

            "Capital"

        ] = (

            capital

            *

            self.portfolio[

                "Score Weight %"

            ]

            /

            100

        ).round(

            2

        )

        return self


    # ---------------------------------------------------------

    def position_rank(self):

        """
        Rank portfolio positions.
        """

        self.portfolio = (

            self.portfolio

            .sort_values(

                "Composite Score",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        self.portfolio.insert(

            0,

            "Portfolio Rank",

            np.arange(

                1,

                len(

                    self.portfolio

                ) + 1

            )

        )

        return self


    # ---------------------------------------------------------

    def portfolio_summary(self):

        """
        Portfolio statistics.
        """

        self.summary = pd.DataFrame(

            {

                "Metric":[

                    "Positions",

                    "Average Composite",

                    "Average Expectancy",

                    "Average Profit Factor",

                    "Total Capital"

                ],

                "Value":[

                    len(

                        self.portfolio

                    ),

                    round(

                        self.portfolio[

                            "Composite Score"

                        ].mean(),

                        2

                    ),

                    round(

                        self.portfolio[

                            "Expectancy"

                        ].mean(),

                        2

                    ),

                    round(

                        self.portfolio[

                            "Profit Factor"

                        ].mean(),

                        2

                    ),

                    round(

                        self.portfolio[

                            "Capital"

                        ].sum(),

                        2

                    )

                ]

            }

        )

        return self
    
    # ---------------------------------------------------------

    def diversification_check(self):

        """
        Calculate portfolio concentration
        using weight distribution.
        """

        self.summary.loc[

            len(self.summary)

        ] = [

            "Largest Position (%)",

            round(

                self.portfolio["Score Weight %"].max(),

                2

            )

        ]

        self.summary.loc[

            len(self.summary)

        ] = [

            "Smallest Position (%)",

            round(

                self.portfolio["Score Weight %"].min(),

                2

            )

        ]

        self.summary.loc[

            len(self.summary)

        ] = [

            "Average Position (%)",

            round(

                self.portfolio["Score Weight %"].mean(),

                2

            )

        ]

        return self


    # ---------------------------------------------------------

    def sector_exposure(self):

        """
        Sector allocation if sector data exists.
        """

        if "Sector" not in self.portfolio.columns:

            self.sector_summary = pd.DataFrame()

            return self

        self.sector_summary = (

            self.portfolio

            .groupby(

                "Sector",

                as_index=False

            )

            .agg(

                Positions=(

                    "Stock",

                    "count"

                ),

                Capital=(

                    "Capital",

                    "sum"

                ),

                Weight=(

                    "Score Weight %",

                    "sum"

                )

            )

            .sort_values(

                "Weight",

                ascending=False

            )

        )

        return self


    # ---------------------------------------------------------

    def apply_position_limit(

        self,

        max_weight=10

    ):

        """
        Cap position weights.
        """

        self.portfolio[

            "Adjusted Weight %"

        ] = (

            self.portfolio[

                "Score Weight %"

            ]

            .clip(

                upper=max_weight

            )

        )

        total = self.portfolio[

            "Adjusted Weight %"

        ].sum()

        self.portfolio[

            "Adjusted Weight %"

        ] = (

            self.portfolio[

                "Adjusted Weight %"

            ]

            /

            total

            *

            100

        ).round(

            2

        )

        return self


    # ---------------------------------------------------------

    def diagnostics(self):

        """
        Portfolio diagnostics.
        """

        print()

        print("=" * 70)

        print("INSTITUTIONAL PORTFOLIO")

        print("=" * 70)

        print(

            f"Positions : {len(self.portfolio)}"

        )

        print(

            f"Capital   : {self.portfolio['Capital'].sum():,.2f}"

        )

        print(

            f"Average Score : "

            f"{self.portfolio['Composite Score'].mean():.2f}"

        )

        print(

            f"Highest Weight : "

            f"{self.portfolio['Adjusted Weight %'].max():.2f}%"

        )

        print("=" * 70)

        print()

        return self


    # ---------------------------------------------------------

    def export(

        self,

        output="Institutional_Portfolio.xlsx"

    ):

        """
        Export workbook.
        """

        with pd.ExcelWriter(

            output,

            engine="openpyxl"

        ) as writer:

            self.portfolio.to_excel(

                writer,

                sheet_name="Portfolio",

                index=False

            )

            self.summary.to_excel(

                writer,

                sheet_name="Summary",

                index=False

            )

            if not self.sector_summary.empty:

                self.sector_summary.to_excel(

                    writer,

                    sheet_name="Sector Allocation",

                    index=False

                )

        return self


    # ---------------------------------------------------------

    def get_results(self):

        """
        Return generated reports.
        """

        return {

            "portfolio": self.portfolio,

            "summary": self.summary,

            "sector": self.sector_summary

        }


    # ---------------------------------------------------------

    def run(

        self,

        capital=100000,

        top_n=25,

        max_weight=10

    ):

        """
        Execute complete portfolio pipeline.
        """

        return (

            self

            .validate()

            .recommendation_filter()

            .top_n(

                top_n

            )

            .equal_weight_portfolio()

            .score_weight_portfolio()

            .allocation_amount(

                capital

            )

            .position_rank()

            .portfolio_summary()

            .diversification_check()

            .sector_exposure()

            .apply_position_limit(

                max_weight

            )

            .diagnostics()

        )


# ==========================================================
# Convenience Function
# ==========================================================

def build_portfolio(

    comparison_df,

    capital=100000,

    top_n=25,

    max_weight=10,

    output_file="Institutional_Portfolio.xlsx"

):

    """
    Build an institutional portfolio.
    """

    engine = (

        PortfolioBuilder(

            comparison_df

        )

        .run(

            capital=capital,

            top_n=top_n,

            max_weight=max_weight

        )

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

        "Import build_portfolio() into strategy_compare.py"

    )