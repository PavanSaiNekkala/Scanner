"""
============================================================
Institutional Strategy Comparison Engine V3
File : relationships/dimensionality_reduction.py

Production Grade Dimensionality Reduction Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.preprocessing import StandardScaler

from core.logger import get_logger

logger = get_logger(__name__)


class DimensionalityReduction:
    """
    Production-grade Dimensionality Reduction Engine.

    Generates

    ✓ PCA
    ✓ Incremental PCA
    ✓ Recommended Components
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
    ):

        df = dataframe.select_dtypes(
            include=np.number
        ).copy()

        # ---------------------------------------------
        # Clean dataset
        # ---------------------------------------------

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True,
        )

        df.dropna(
            axis=1,
            how="all",
            inplace=True,
        )

        if not df.empty:

            df = df.fillna(
                df.median(
                    numeric_only=True
                )
            )

            # Remove constant columns

            df = df.loc[
                :,
                df.nunique(dropna=False) > 1
            ]

        self.df = df

        self.scaler = StandardScaler()

        self.X = None

        if (
            self.df.shape[0] >= 2
            and
            self.df.shape[1] >= 2
        ):

            try:

                self.X = self.scaler.fit_transform(
                    self.df
                )

            except Exception as exc:

                logger.warning(
                    "Scaling failed: %s",
                    exc,
                )

                self.X = None

    # ==================================================
    # INTERNAL
    # ==================================================

    def _ready(self):

        return self.X is not None

    # ==================================================
    # PCA
    # ==================================================

    def pca(
        self,
        n_components=None,
    ):

        logger.info(
            "Running PCA..."
        )

        if not self._ready():

            return {
                "Scores": pd.DataFrame(),
                "Variance": pd.DataFrame(),
                "Loadings": pd.DataFrame(),
            }

        max_components = min(
            self.X.shape[0],
            self.X.shape[1],
        )

        if n_components is None:

            n_components = max_components

        else:

            n_components = min(
                n_components,
                max_components,
            )

        try:

            model = PCA(
                n_components=n_components,
                random_state=42,
            )

            transformed = model.fit_transform(
                self.X
            )

            scores = pd.DataFrame(
                transformed,
                columns=[
                    f"PC{i+1}"
                    for i in range(
                        transformed.shape[1]
                    )
                ],
            )

            variance = pd.DataFrame(
                {
                    "Principal Component": scores.columns,
                    "Explained Variance":
                        model.explained_variance_,
                    "Explained Variance Ratio":
                        model.explained_variance_ratio_,
                    "Cumulative Variance":
                        np.cumsum(
                            model.explained_variance_ratio_
                        ),
                }
            )

            loadings = pd.DataFrame(
                model.components_.T,
                index=self.df.columns,
                columns=scores.columns,
            )

            return {
                "Scores": scores,
                "Variance": variance,
                "Loadings": loadings,
            }

        except Exception as exc:

            logger.warning(
                "PCA failed: %s",
                exc,
            )

            return {
                "Scores": pd.DataFrame(),
                "Variance": pd.DataFrame(),
                "Loadings": pd.DataFrame(),
            }

    # ==================================================
    # INCREMENTAL PCA
    # ==================================================

    def incremental_pca(
        self,
        n_components=None,
    ):

        logger.info(
            "Running Incremental PCA..."
        )

        if not self._ready():

            return pd.DataFrame()

        max_components = min(
            self.X.shape[0],
            self.X.shape[1],
        )

        if n_components is None:

            n_components = max_components

        else:

            n_components = min(
                n_components,
                max_components,
            )

        try:

            model = IncrementalPCA(
                n_components=n_components
            )

            transformed = model.fit_transform(
                self.X
            )

            return pd.DataFrame(
                transformed,
                columns=[
                    f"IPC{i+1}"
                    for i in range(
                        transformed.shape[1]
                    )
                ],
            )

        except Exception as exc:

            logger.warning(
                "Incremental PCA failed: %s",
                exc,
            )

            return pd.DataFrame()

    # ==================================================
    # RECOMMENDED COMPONENTS
    # ==================================================

    def recommended_components(
        self,
        threshold=0.95,
    ):

        if not self._ready():

            return pd.DataFrame(
                {
                    "Threshold": [threshold],
                    "Recommended Components": [0],
                }
            )

        try:

            model = PCA()

            model.fit(self.X)

            cumulative = np.cumsum(
                model.explained_variance_ratio_
            )

            n = (
                np.argmax(
                    cumulative >= threshold
                )
                + 1
            )

            return pd.DataFrame(
                {
                    "Threshold": [threshold],
                    "Recommended Components": [n],
                }
            )

        except Exception as exc:

            logger.warning(
                "Recommendation failed: %s",
                exc,
            )

            return pd.DataFrame(
                {
                    "Threshold": [threshold],
                    "Recommended Components": [0],
                }
            )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self):

        logger.info(
            "Generating Dimensionality Reduction Report..."
        )

        return {

            "PCA":
                self.pca(),

            "Incremental PCA":
                self.incremental_pca(),

            "Recommendation":
                self.recommended_components(),

        }


if __name__ == "__main__":

    print(
        "Import DimensionalityReduction from relationship_engine.py"
    )