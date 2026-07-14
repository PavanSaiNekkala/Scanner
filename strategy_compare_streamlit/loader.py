from pathlib import Path

import pandas as pd


class StrategyLoader:

    def __init__(

        self,

        folder

    ):

        self.folder = Path(

            folder

        )

    def load(self):

        reports = {}

        files = sorted(

            self.folder.glob(

                "Output*.xlsx"

            )

        )

        print("=" * 60)
        print("Loading Reports")
        print("=" * 60)

        for file in files:

            print(file.name)

            df = pd.read_excel(

                file

            )

            reports[file.stem] = df

        print()

        print(

            f"Total Reports Loaded : {len(reports)}"

        )

        return reports