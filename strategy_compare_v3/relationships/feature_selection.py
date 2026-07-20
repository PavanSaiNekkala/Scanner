"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/feature_selection.py

Feature Selection Engine

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.feature_selection import (
    VarianceThreshold,
    SelectKBest,
    f_regression,
    mutual_info_regression,
)

from sklearn.ensemble import RandomForestRegressor


from core.logger import get_logger

logger = get_logger(__name__)


class FeatureSelection:
    """
    Institutional Feature Selection Engine.
    """

    def __init__(self, dataframe: pd.DataFrame, target: str):
        self.df = dataframe.copy()

        self.target = target

        if target not in self.df.columns:
            raise ValueError(f"Target column '{target}' not found.")

        self.X = self.df.drop(columns=[target])

        self.y = self.df[target]

        self.X = self.X.select_dtypes(include=np.number)

        self.X = self.X.fillna(self.X.median(numeric_only=True))

        self.y = self.y.fillna(self.y.median())

    # --------------------------------------------------

    def variance_threshold(self):
        logger.info("Running Variance Threshold...")

        selector = VarianceThreshold()

        selector.fit(self.X)

        return (
            pd.DataFrame({"Feature": self.X.columns, "Variance": selector.variances_})
            .sort_values("Variance", ascending=False)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def anova(self):
        logger.info("Running ANOVA...")

        selector = SelectKBest(score_func=f_regression, k="all")

        selector.fit(self.X, self.y)

        return (
            pd.DataFrame(
                {
                    "Feature": self.X.columns,
                    "F Score": selector.scores_,
                    "P Value": selector.pvalues_,
                }
            )
            .sort_values("F Score", ascending=False)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def mutual_information(self):
        logger.info("Running Mutual Information...")

        scores = mutual_info_regression(self.X, self.y, random_state=42)

        return (
            pd.DataFrame({"Feature": self.X.columns, "Mutual Information": scores})
            .sort_values("Mutual Information", ascending=False)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def random_forest(self):
        logger.info("Running Random Forest...")

        model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)

        model.fit(self.X, self.y)

        return (
            pd.DataFrame(
                {"Feature": self.X.columns, "Importance": model.feature_importances_}
            )
            .sort_values("Importance", ascending=False)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def correlation(self):
        corr = self.df.corr(numeric_only=True)[self.target]

        corr = corr.drop(self.target)

        return (
            pd.DataFrame(
                {
                    "Feature": corr.index,
                    "Correlation": corr.values,
                    "Absolute": np.abs(corr.values),
                }
            )
            .sort_values("Absolute", ascending=False)
            .reset_index(drop=True)
        )

    # --------------------------------------------------

    def generate(self):
        logger.info("Generating Feature Selection Report...")

        return {
            "Variance": self.variance_threshold(),
            "ANOVA": self.anova(),
            "Mutual Information": self.mutual_information(),
            "Correlation": self.correlation(),
            "Random Forest": self.random_forest(),
        }


if __name__ == "__main__":
    print("Import inside relationship_engine.py")
