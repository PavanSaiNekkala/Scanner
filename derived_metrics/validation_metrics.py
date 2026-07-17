"""
===============================================================
Institutional Strategy Comparison Engine V3

Module
------
validation_metrics.py

Purpose
-------
Institutional-grade validation, anomaly detection,
and data quality scoring.

===============================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ============================================================
# Utility Functions
# ============================================================

def numeric(series):

    return pd.to_numeric(

        series,

        errors="coerce"

    )


def safe_divide(a, b):

    a = numeric(a)

    b = numeric(b)

    return np.where(

        (b == 0)

        |

        (pd.isna(b)),

        np.nan,

        a / b

    )


# ============================================================
# Validation Engine
# ============================================================

class ValidationMetrics:

    def __init__(self, df):

        self.df = df.copy()

    # ---------------------------------------------------------

    def prepare_columns(self):

        numeric_cols = [

            "Trades",

            "Win%",

            "Expectancy",

            "Profit Factor",

            "Reward Risk",

            "Annual Return %",

            "Avg days",

            "Years"

        ]

        for col in numeric_cols:

            if col in self.df.columns:

                self.df[col] = numeric(

                    self.df[col]

                )

        return self
    
    # ---------------------------------------------------------

    def zscore_outlier_detection(self):
        """
        Detect outliers using Z-score.
        """

        cols = [

            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %"

        ]

        outliers = np.zeros(len(self.df), dtype=int)

        for col in cols:

            if col not in self.df.columns:

                continue

            std = self.df[col].std()

            if pd.isna(std) or std == 0:

                continue

            z = (

                self.df[col]

                -

                self.df[col].mean()

            ) / std

            outliers += (

                np.abs(z) > 3

            ).astype(int)

        self.df["ZScore Outliers"] = outliers

        return self

    # ---------------------------------------------------------

    def iqr_outlier_detection(self):
        """
        Detect IQR outliers.
        """

        cols = [

            "Expectancy",
            "Profit Factor",
            "Reward Risk",
            "Annual Return %"

        ]

        outliers = np.zeros(len(self.df), dtype=int)

        for col in cols:

            if col not in self.df.columns:

                continue

            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers += (

                (

                    self.df[col] < lower

                )

                |

                (

                    self.df[col] > upper

                )

            ).astype(int)

        self.df["IQR Outliers"] = outliers

        return self

    # ---------------------------------------------------------

    def completeness_score(self):
        """
        Data completeness score.
        """

        self.df["Completeness Score"] = (

            100

            -

            self.df["Missing %"]

        )

        return self

    # ---------------------------------------------------------

    def logical_integrity(self):
        """
        Logical consistency checks.
        """

        errors = np.zeros(

            len(self.df),

            dtype=int

        )

        if "Win%" in self.df:

            errors += (

                (

                    self.df["Win%"] < 0

                )

                |

                (

                    self.df["Win%"] > 100

                )

            ).astype(int)

        if "Profit Factor" in self.df:

            errors += (

                self.df["Profit Factor"] <= 0

            ).astype(int)

        if "Reward Risk" in self.df:

            errors += (

                self.df["Reward Risk"] <= 0

            ).astype(int)

        self.df["Logical Errors"] = errors

        return self

    # ---------------------------------------------------------

    def extreme_return_flag(self):
        """
        Flag unrealistic returns.
        """

        self.df["Extreme Return"] = (

            self.df["Annual Return %"]

            > 500

        )

        return self

    # ---------------------------------------------------------

    def extreme_expectancy_flag(self):
        """
        Flag unrealistic expectancy.
        """

        self.df["Extreme Expectancy"] = (

            self.df["Expectancy"]

            > 50

        )

        return self

    # ---------------------------------------------------------

    def statistical_reliability(self):
        """
        Reliability based on sample size.
        """

        self.df["Statistical Reliability"] = np.minimum(

            self.df["Trades"]

            / 100,

            1

        ) * 100

        return self

    # ---------------------------------------------------------

    def consistency_score(self):
        """
        Overall consistency.
        """

        penalties = (

            self.df["Logical Errors"]

            +

            self.df["ZScore Outliers"]

            +

            self.df["IQR Outliers"]

        )

        self.df["Validation Consistency"] = (

            100

            -

            penalties * 10

        ).clip(

            lower=0,

            upper=100

        )

        return self

    # ---------------------------------------------------------

    def confidence_score(self):
        """
        Confidence in data quality.
        """

        self.df["Data Confidence"] = (

            self.df["Completeness Score"]

            * 0.40

            +

            self.df["Validation Consistency"]

            * 0.30

            +

            self.df["Statistical Reliability"]

            * 0.30

        )

        return self

    # ---------------------------------------------------------

    def institutional_validation_score(self):
        """
        Final validation score.
        """

        self.df["Institutional Validation Score"] = (

            self.df["Data Confidence"]

            * 0.60

            +

            self.df["Completeness Score"]

            * 0.20

            +

            self.df["Validation Consistency"]

            * 0.20

        )

        return self
    
    # ---------------------------------------------------------

    def validation_grade(self):
        """
        Assign institutional validation grade.
        """

        score = self.df["Institutional Validation Score"]

        self.df["Validation Grade"] = np.select(

            [

                score >= 95,

                score >= 90,

                score >= 80,

                score >= 70,

                score >= 60

            ],

            [

                "Excellent",

                "Very Good",

                "Good",

                "Fair",

                "Poor"

            ],

            default="Critical"

        )

        return self

    # ---------------------------------------------------------

    def validation_status(self):
        """
        Overall validation status.
        """

        critical = (

            self.df["Zero Trades"]

            |

            self.df["Invalid Win%"]

            |

            self.df["Invalid Reward Risk"]

            |

            self.df["Invalid Profit Factor"]

            |

            self.df["Invalid Holding"]

            |

            self.df["Invalid Years"]

        )

        warnings = (

            (self.df["Missing %"] > 5)

            |

            (self.df["Logical Errors"] > 0)

            |

            (self.df["ZScore Outliers"] > 0)

            |

            (self.df["IQR Outliers"] > 0)

        )

        self.df["Validation Status"] = np.select(

            [

                critical,

                warnings

            ],

            [

                "FAILED",

                "WARNING"

            ],

            default="PASSED"

        )

        return self

    # ---------------------------------------------------------

    def validation_rank(self):
        """
        Rank datasets by validation quality.
        """

        self.df["Validation Rank"] = (

            self.df["Institutional Validation Score"]

            .rank(

                ascending=False,

                method="dense"

            )

            .astype(int)

        )

        return self

    # ---------------------------------------------------------

    def normalize_scores(self):
        """
        Normalize major validation scores.
        """

        metrics = [

            "Completeness Score",

            "Validation Consistency",

            "Statistical Reliability",

            "Data Confidence",

            "Institutional Validation Score"

        ]

        for metric in metrics:

            if metric not in self.df.columns:

                continue

            minimum = self.df[metric].min()
            maximum = self.df[metric].max()

            if pd.isna(minimum) or pd.isna(maximum):

                continue

            if minimum == maximum:

                self.df[f"{metric} (Norm)"] = 50.0

            else:

                self.df[f"{metric} (Norm)"] = (

                    (

                        self.df[metric]

                        -

                        minimum

                    )

                    /

                    (

                        maximum

                        -

                        minimum

                    )

                    * 100

                )

        return self

    # ---------------------------------------------------------

    def cleanup(self):
        """
        Remove invalid values.
        """

        self.df.replace(

            [

                np.inf,

                -np.inf

            ],

            np.nan,

            inplace=True

        )

        return self

    # ---------------------------------------------------------

    def round_metrics(self):
        """
        Round validation metrics.
        """

        cols = [

            "Missing %",
            "Completeness Score",
            "Statistical Reliability",
            "Validation Consistency",
            "Data Confidence",
            "Institutional Validation Score"

        ]

        for col in cols:

            if col in self.df.columns:

                self.df[col] = (

                    self.df[col]

                    .round(2)

                )

        return self

    # ---------------------------------------------------------

    def run(self):

        return (

            self.prepare_columns()

                .missing_values()

                .missing_percent()

                .duplicate_rows()

                .zero_trade_flag()

                .invalid_win_rate()

                .invalid_reward_risk()

                .invalid_profit_factor()

                .invalid_holding_period()

                .invalid_years()

                .zscore_outlier_detection()

                .iqr_outlier_detection()

                .completeness_score()

                .logical_integrity()

                .extreme_return_flag()

                .extreme_expectancy_flag()

                .statistical_reliability()

                .consistency_score()

                .confidence_score()

                .institutional_validation_score()

                .validation_grade()

                .validation_status()

                .validation_rank()

                .normalize_scores()

                .cleanup()

                .round_metrics()

                .df

        )


# ============================================================
# Convenience Function
# ============================================================

def derive_validation_metrics(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Derive institutional validation metrics.

    Parameters
    ----------
    df : pandas.DataFrame
        Strategy comparison dataset.

    Returns
    -------
    pandas.DataFrame
        DataFrame with validation metrics appended.
    """

    return ValidationMetrics(df).run()