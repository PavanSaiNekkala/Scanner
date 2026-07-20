"""
Input Validation Module
"""

from pathlib import Path

import pandas as pd

from config import (
    INPUT_PATTERN,
    PRIMARY_METRICS,
    REQUIRED_COLUMNS,
    RECOMMENDATION_RULES,
)

from utils import check_columns

###########################################################################
# VALIDATOR
###########################################################################


class StrategyValidator:
    def __init__(self, folder):
        self.folder = Path(folder)

    ###########################################################################
    # VALIDATE ALL REPORTS
    ###########################################################################

    def validate(self):
        reports = sorted(self.folder.glob(INPUT_PATTERN))

        if len(reports) == 0:
            raise FileNotFoundError("No strategy reports found.")

        errors = []

        for report in reports:
            issues = self.validate_file(report)

            if issues:
                errors.extend(issues)

        return errors

    ###########################################################################
    # VALIDATE SINGLE FILE
    ###########################################################################

    def validate_file(self, filepath):
        issues = []

        try:
            df = pd.read_excel(filepath)

        except Exception as e:
            issues.append(f"{filepath.name}: Unable to read file ({e})")

            return issues

        #######################################################################
        # EMPTY
        #######################################################################

        if df.empty:
            issues.append(f"{filepath.name}: Report is empty.")

            return issues

        #######################################################################
        # REQUIRED COLUMNS
        #######################################################################

        missing = check_columns(df, REQUIRED_COLUMNS)

        if missing:
            issues.append(f"{filepath.name}: Missing columns -> " + ", ".join(missing))

            return issues

        #######################################################################
        # PRIMARY METRICS
        #######################################################################

        metric_missing = [
            metric for metric in PRIMARY_METRICS if metric not in df.columns
        ]

        if metric_missing:
            issues.append(
                f"{filepath.name}: Missing metrics -> " + ", ".join(metric_missing)
            )

        #######################################################################
        # NUMERIC METRICS
        #######################################################################

        for metric in PRIMARY_METRICS:
            if metric not in df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(df[metric]):
                issues.append(f"{filepath.name}: '{metric}' must be numeric.")

        #######################################################################
        # EMPTY STOCK COLUMN
        #######################################################################

        if df["Stock"].isna().all():
            issues.append(f"{filepath.name}: Stock column is empty.")

        #######################################################################
        # EMPTY SCORE
        #######################################################################

        if df["Overall Score"].isna().all():
            issues.append(f"{filepath.name}: Overall Score column is empty.")

        #######################################################################
        # SCORE RANGE
        #######################################################################

        invalid_scores = df[(df["Overall Score"] < 0) | (df["Overall Score"] > 100)]

        if not invalid_scores.empty:
            issues.append(f"{filepath.name}: Overall Score must be between 0 and 100.")

        #######################################################################
        # DUPLICATE STOCKS
        #######################################################################

        duplicate_stock = df.duplicated(subset=["Stock"]).sum()

        if duplicate_stock > 0:
            issues.append(
                f"{filepath.name}: {duplicate_stock} duplicate stock(s) detected."
            )

        #######################################################################
        # DUPLICATE RANKS
        #######################################################################

        duplicate_rank = df.duplicated(subset=["Strategy Rank"]).sum()

        if duplicate_rank > 0:
            issues.append(
                f"{filepath.name}: {duplicate_rank} duplicate Strategy Rank value(s)."
            )

        #######################################################################
        # RECOMMENDATION VALUES
        #######################################################################

        allowed = {
            str(value).strip().upper() for value in RECOMMENDATION_RULES.values()
        }

        recommendations = (
            df["Recommendation"].fillna("").astype(str).str.strip().str.upper()
        )

        invalid_recommendation = df.loc[~recommendations.isin(allowed)]

        if not invalid_recommendation.empty:
            issues.append(f"{filepath.name}: Invalid Recommendation values found.")

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):
        reports = sorted(self.folder.glob(INPUT_PATTERN))

        errors = self.validate()

        status = "PASS" if len(errors) == 0 else "FAIL"

        message = (
            "All reports validated successfully."
            if status == "PASS"
            else "Validation errors detected."
        )

        return {
            "Status": status,
            "Message": message,
            "Files Checked": len(reports),
            "Errors Found": len(errors),
            "Errors": errors,
        }
