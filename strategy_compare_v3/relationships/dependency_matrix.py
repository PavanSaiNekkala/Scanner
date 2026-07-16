"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/dependency_matrix.py

Dependency Matrix Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.feature_selection import mutual_info_regression

from core.logger import get_logger

logger = get_logger(__name__)


class DependencyMatrix:

    """
    Generates dependency matrices among all
    numeric variables.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe.select_dtypes(
            include=np.number
        ).copy()

    # --------------------------------------------------

    def covariance(self):

        logger.info(
            "Computing covariance matrix..."
        )

        return self.df.cov()

    # --------------------------------------------------

    def mutual_information(self):

        logger.info(
            "Computing mutual information..."
        )

        cols = self.df.columns

        mi = pd.DataFrame(

            index=cols,

            columns=cols,

            dtype=float

        )

        for target in cols:

            X = self.df.drop(
                columns=target
            )

            y = self.df[target]

            scores = mutual_info_regression(

                X,

                y,

                random_state=42

            )

            mi.loc[target, target] = 1.0

            mi.loc[target, X.columns] = scores

        return mi.fillna(0)

    # --------------------------------------------------

    def dependency_strength(self):

        corr = self.df.corr()

        rows = []

        cols = corr.columns

        for i in range(len(cols)):

            for j in range(i + 1, len(cols)):

                value = corr.iloc[i, j]

                rows.append({

                    "Feature A":

                        cols[i],

                    "Feature B":

                        cols[j],

                    "Correlation":

                        round(
                            value,
                            4
                        ),

                    "Absolute":

                        round(
                            abs(value),
                            4
                        ),

                    "Strength":

                        (

                            "Very Strong"

                            if abs(value) >= 0.90

                            else

                            "Strong"

                            if abs(value) >= 0.70

                            else

                            "Moderate"

                            if abs(value) >= 0.50

                            else

                            "Weak"

                        )

                })

        report = pd.DataFrame(rows)

        report = report.sort_values(

            "Absolute",

            ascending=False

        )

        return report.reset_index(drop=True)

    # --------------------------------------------------

    def generate(self):

        logger.info(

            "Generating dependency matrices..."

        )

        return {

            "Covariance":

                self.covariance(),

            "Mutual Information":

                self.mutual_information(),

            "Dependency Strength":

                self.dependency_strength()

        }


if __name__ == "__main__":

    print(
        "Import inside relationship_engine.py"
    )