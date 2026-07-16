"""
Strategy Report Loader
"""

from pathlib import Path

import pandas as pd

from config import INPUT_PATTERN

from logger import StrategyLogger


###########################################################################
# LOADER
###########################################################################

class StrategyLoader:

    def __init__(

        self,

        folder

    ):

        self.folder = Path(

            folder

        )

        self.logger = StrategyLogger()

    ###########################################################################
    # LOAD REPORTS
    ###########################################################################

    def load(self):

        reports = {}

        files = sorted(

            self.folder.glob(

                INPUT_PATTERN

            )

        )

        if len(

            files

        ) == 0:

            raise FileNotFoundError(

                f"No reports found in {self.folder}"

            )

        self.logger.separator()

        self.logger.info(

            "Loading Strategy Reports"

        )

        self.logger.separator()

        for file in files:

            try:

                self.logger.info(

                    f"Loading : {file.name}"

                )

                dataframe = pd.read_excel(

                    file

                )

                if dataframe.empty:

                    self.logger.warning(

                        f"{file.name} is empty. Skipping."

                    )

                    continue

                reports[

                    file.stem

                ] = dataframe

                self.logger.info(

                    f"Loaded : {dataframe.shape[0]} rows × {dataframe.shape[1]} columns"

                )

            except Exception as e:

                self.logger.error(

                    f"Failed to load {file.name}: {e}"

                )

        if len(

            reports

        ) == 0:

            raise RuntimeError(

                "No valid strategy reports were loaded."

            )

        self.logger.separator()

        self.logger.info(

            f"Total Reports Loaded : {len(reports)}"

        )

        self.logger.separator()

        return reports