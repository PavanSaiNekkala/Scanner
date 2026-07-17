"""
===============================================================
Institutional Strategy Comparison Engine V3

Master Derived Metrics Engine

Author
------
OpenAI

===============================================================
"""

from __future__ import annotations

import pandas as pd

from derived_metrics.performance_metrics import (
    derive_performance_metrics,
)

from derived_metrics.risk_metrics import (
    derive_risk_metrics,
)

from derived_metrics.exit_metrics import (
    derive_exit_metrics,
)

from derived_metrics.opportunity_metrics import (
    derive_opportunity_metrics,
)

from derived_metrics.efficiency_metrics import (
    derive_efficiency_metrics,
)

from derived_metrics.validation_metrics import (
    derive_validation_metrics,
)

from derived_metrics.scoring_metrics import (
    derive_scoring_metrics,
)

class DerivedMetricsEngine:

    """
    Master Institutional Metrics Engine

    Pipeline

    Validation
          ↓
    Performance
          ↓
    Risk
          ↓
    Exit
          ↓
    Opportunity
          ↓
    Efficiency
          ↓
    Institutional Scoring

    """

    def __init__(self, df):

        self.df = df.copy()


    # -----------------------------------------------------

    def validation_stage(self):

        print(
            "Running Validation Metrics..."
        )

        self.df = derive_validation_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def performance_stage(self):

        print(

            "Running Performance Metrics..."

        )

        self.df = derive_performance_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def risk_stage(self):

        print(

            "Running Risk Metrics..."

        )

        self.df = derive_risk_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def exit_stage(self):

        print(

            "Running Exit Metrics..."

        )

        self.df = derive_exit_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def opportunity_stage(self):

        print(

            "Running Opportunity Metrics..."

        )

        self.df = derive_opportunity_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def efficiency_stage(self):

        print(

            "Running Efficiency Metrics..."

        )

        self.df = derive_efficiency_metrics(

            self.df

        )

        return self
    
    # -----------------------------------------------------

    def scoring_stage(self):

        print(

            "Running Institutional Scoring..."

        )

        self.df = derive_scoring_metrics(

            self.df

        )

        return self

    # -----------------------------------------------------

    def pipeline_summary(self):

        """
        Build execution summary.
        """

        self.summary = {

            "Rows Processed": len(self.df),

            "Columns Produced": len(self.df.columns),

            "Passed Validation": int(

                (self.df["Validation Status"] == "PASSED").sum()

            )

            if "Validation Status" in self.df.columns

            else None,

            "Warning Rows": int(

                (self.df["Validation Status"] == "WARNING").sum()

            )

            if "Validation Status" in self.df.columns

            else None,

            "Failed Validation": int(

                (self.df["Validation Status"] == "FAILED").sum()

            )

            if "Validation Status" in self.df.columns

            else None,

        }

        return self

    # -----------------------------------------------------

    def diagnostics(self):

        """
        Generate institutional diagnostics.
        """

        diagnostics = {}

        if "Composite Score" in self.df.columns:

            diagnostics["Average Composite"] = round(

                self.df["Composite Score"].mean(),

                2

            )

            diagnostics["Maximum Composite"] = round(

                self.df["Composite Score"].max(),

                2

            )

            diagnostics["Minimum Composite"] = round(

                self.df["Composite Score"].min(),

                2

            )

        if "Recommendation" in self.df.columns:

            diagnostics["Recommendations"] = (

                self.df["Recommendation"]

                .value_counts()

                .to_dict()

            )

        self.diagnostics_report = diagnostics

        return self

    # -----------------------------------------------------

    def execution_report(self):

        """
        Print execution summary.
        """

        print("\n" + "=" * 60)

        print("Institutional Metrics Engine Completed")

        print("=" * 60)

        for key, value in self.summary.items():

            print(

                f"{key:<25}: {value}"

            )

        print()

        for key, value in self.diagnostics_report.items():

            print(

                f"{key:<25}: {value}"

            )

        print("=" * 60)

        print()

        return self

    # -----------------------------------------------------

    def validate_dependencies(self):

        """
        Verify critical columns exist before scoring.
        """

        required = [

            "Expectancy",

            "Profit Factor",

            "Reward Risk",

            "Institutional Exit Score",

            "Institutional Opportunity Score",

            "Institutional Efficiency Score",

        ]

        missing = [

            col

            for col in required

            if col not in self.df.columns

        ]

        if missing:

            raise ValueError(

                "Missing derived columns:\n"

                + "\n".join(missing)

            )

        return self

    # -----------------------------------------------------

    def sort_results(self):

        """
        Sort final output.
        """

        if "Institution Rank" in self.df.columns:

            self.df = self.df.sort_values(

                "Institution Rank"

            )

        elif "Composite Score" in self.df.columns:

            self.df = self.df.sort_values(

                "Composite Score",

                ascending=False

            )

        self.df = self.df.reset_index(

            drop=True

        )

        return self

    # -----------------------------------------------------

    def get_dataframe(self):

        """
        Return processed dataframe.
        """

        return self.df

    # -----------------------------------------------------

    def run(self):
        """
        Execute the complete institutional pipeline.
        """

        import time

        start = time.perf_counter()

        try:

            (

                self.validation_stage()

                    .performance_stage()

                    .risk_stage()

                    .exit_stage()

                    .opportunity_stage()

                    .efficiency_stage()

                    .validate_dependencies()

                    .scoring_stage()

                    .pipeline_summary()

                    .diagnostics()

                    .sort_results()

            )

        except Exception as exc:

            raise RuntimeError(

                f"Derived Metrics Engine failed:\n{exc}"

            ) from exc

        finally:

            self.execution_time = round(

                time.perf_counter() - start,

                3

            )

        self.summary["Execution Time (s)"] = (

            self.execution_time

        )

        self.execution_report()

        return self.df


# ===========================================================
# Convenience Function
# ===========================================================

def derive_metrics(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Execute the complete institutional
    metrics pipeline.
    """

    return DerivedMetricsEngine(df).run()


# ===========================================================
# File Processing
# ===========================================================

def process_file(
    input_file: str,
    output_file: str = None
):
    """
    Process a single CSV/Excel file.
    """

    import os

    print(f"\nLoading {input_file}")

    extension = os.path.splitext(

        input_file

    )[1].lower()

    if extension == ".csv":

        df = pd.read_csv(

            input_file

        )

    elif extension in [

        ".xlsx",

        ".xls"

    ]:

        df = pd.read_excel(

            input_file

        )

    else:

        raise ValueError(

            f"Unsupported file type: {extension}"

        )

    result = derive_metrics(df)

    if output_file is None:

        base = os.path.splitext(

            input_file

        )[0]

        output_file = (

            base

            +

            "_Institutional.xlsx"

        )

    result.to_excel(

        output_file,

        index=False

    )

    print(

        f"Saved → {output_file}"

    )

    return result


# ===========================================================
# Directory Processing
# ===========================================================

def process_directory(
    directory
):
    """
    Process every CSV/Excel file
    in a directory.
    """

    from pathlib import Path

    directory = Path(directory)

    files = []

    files.extend(

        directory.glob("*.csv")

    )

    files.extend(

        directory.glob("*.xlsx")

    )

    files.extend(

        directory.glob("*.xls")

    )

    if not files:

        print(

            "No files found."

        )

        return

    print(

        f"\nFound {len(files)} files."

    )

    for file in sorted(files):

        try:

            process_file(

                str(file)

            )

        except Exception as exc:

            print(

                f"Failed: {file.name}"

            )

            print(exc)


# ===========================================================
# Main
# ===========================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(

        description=(
            "Institutional Strategy "
            "Comparison Engine V3"
        )

    )

    parser.add_argument(

        "--file",

        type=str,

        help="Input CSV or Excel file"

    )

    parser.add_argument(

        "--dir",

        type=str,

        help="Directory containing reports"

    )

    args = parser.parse_args()

    if args.file:

        process_file(

            args.file

        )

    elif args.dir:

        process_directory(

            args.dir

        )

    else:

        parser.print_help()