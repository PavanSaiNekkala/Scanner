import pandas as pd

from config import *
from utils import safe_numeric


class StrategyLoader:
    def __init__(self):
        self.files = sorted(INPUT_DIR.glob("*.xlsx"))

        self.strategies = {}

    def load(self):
        if len(self.files) == 0:
            raise FileNotFoundError("No strategy reports found.")

        for file in self.files:
            strategy = file.stem

            strategy = strategy.replace("Output_backtest_", "")

            strategy = strategy.replace("_Report", "")

            df = pd.read_excel(file)

            df.columns = [str(c).strip() for c in df.columns]

            for col in PRIMARY_METRICS:
                if col in df.columns:
                    df[col] = safe_numeric(df[col])

            self.strategies[strategy] = df

        return self.strategies

    def common_columns(self):
        cols = []

        for df in self.strategies.values():
            cols.append(set(df.columns))

        return sorted(list(set.intersection(*cols)))
