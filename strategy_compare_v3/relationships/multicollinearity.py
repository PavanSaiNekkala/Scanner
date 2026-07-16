"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/multicollinearity.py

Multicollinearity Analysis Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor
)

from numpy.linalg import eigvals

from core.logger import get_logger

logger = get_logger(__name__)


class Multicollinearity:

    """
    Detect multicollinearity among numeric features.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.select_dtypes(
            include=np.number
        ).copy()

        self.df = self.df.dropna()

    # --------------------------------------------------

    def vif(self):

        logger.info(
            "Calculating VIF..."
        )

        X = self.df.copy()

        report = []

        for i, col in enumerate(X.columns):

            report.append({

                "Feature":

                    col,

                "VIF":

                    round(

                        variance_inflation_factor(

                            X.values,

                            i

                        ),

                        4

                    )

            })

        report = pd.DataFrame(report)

        report["Severity"] = np.select(

            [

                report["VIF"] < 5,

                report["VIF"] < 10,

            ],

            [

                "Low",

                "Moderate"

            ],

            default="High"

        )

        return report.sort_values(

            "VIF",

            ascending=False

        ).reset_index(drop=True)

    # --------------------------------------------------

    def correlation_redundancy(

        self,

        threshold=0.95

    ):

        corr = self.df.corr().abs()

        upper = corr.where(

            np.triu(

                np.ones(corr.shape),

                k=1

            ).astype(bool)

        )

        redundant = []

        for column in upper.columns:

            high = upper.index[

                upper[column] >= threshold

            ].tolist()

            if high:

                redundant.append({

                    "Feature":

                        column,

                    "Highly Correlated With":

                        ", ".join(high)

                })

        return pd.DataFrame(redundant)

    # --------------------------------------------------

    def eigenvalues(self):

        corr = self.df.corr()

        values = eigvals(corr)

        return pd.DataFrame({

            "Eigenvalue":

                values.real

        }).sort_values(

            "Eigenvalue",

            ascending=False

        ).reset_index(drop=True)

    # --------------------------------------------------

    def condition_number(self):

        corr = self.df.corr()

        eig = eigvals(corr)

        eig = np.real(eig)

        condition = np.sqrt(

            eig.max()

            /

            eig.min()

        )

        return round(

            float(condition),

            4

        )

    # --------------------------------------------------

    def generate(self):

        logger.info(

            "Generating multicollinearity report..."

        )

        return {

            "VIF":

                self.vif(),

            "Redundant Features":

                self.correlation_redundancy(),

            "Eigenvalues":

                self.eigenvalues(),

            "Condition Number":

                pd.DataFrame({

                    "Metric":

                        ["Condition Number"],

                    "Value":

                        [

                            self.condition_number()

                        ]

                })

        }


if __name__ == "__main__":

    print(

        "Import inside relationship_engine.py"

    )