"""
Input Validation Module
"""

from pathlib import Path

import pandas as pd

from config import PRIMARY_METRICS

from utils import check_columns


###########################################################################
# VALIDATOR
###########################################################################

class StrategyValidator:

    def __init__(

        self,

        folder

    ):

        self.folder = Path(

            folder

        )

    ###########################################################################
    # VALIDATE ALL FILES
    ###########################################################################

    def validate(self):

        reports = sorted(

            self.folder.glob(

                "*.xlsx"

            )

        )

        if len(reports) == 0:

            raise FileNotFoundError(

                "No strategy reports found."

            )

        errors = []

        for report in reports:

            status = self.validate_file(

                report

            )

            if status:

                errors.extend(

                    status

                )

        return errors

    ###########################################################################
    # VALIDATE SINGLE FILE
    ###########################################################################

    def validate_file(

        self,

        filepath

    ):

        issues = []

        try:

            df = pd.read_excel(

                filepath

            )

        except Exception as e:

            issues.append(

                f"{filepath.name}: {e}"

            )

            return issues

        if df.empty:

            issues.append(

                f"{filepath.name}: Empty report."

            )

            return issues

        required = [

            "Strategy Rank",

            "Stock",

            "Overall Score",

            "Recommendation"

        ]

        missing = check_columns(

            df,

            required

        )

        if missing:

            issues.append(

                f"{filepath.name}: Missing columns -> {', '.join(missing)}"

            )

        metric_missing = [

            metric

            for metric in PRIMARY_METRICS

            if metric not in df.columns

        ]

        if metric_missing:

            issues.append(

                f"{filepath.name}: Missing metrics -> {', '.join(metric_missing)}"

            )

        if df["Stock"].isna().all():

            issues.append(

                f"{filepath.name}: Stock column is empty."

            )

        if df["Overall Score"].isna().all():

            issues.append(

                f"{filepath.name}: Overall Score column is empty."

            )

        duplicate = df.duplicated(

            subset=["Stock"]

        ).sum()

        if duplicate > 0:

            issues.append(

                f"{filepath.name}: {duplicate} duplicate stocks."

            )

        return issues

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):

        errors = self.validate()

        if len(errors) == 0:

            return {

                "Status": "PASS",

                "Errors": []

            }

        return {

            "Status": "FAIL",

            "Errors": errors

        }