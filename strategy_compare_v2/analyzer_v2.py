import pandas as pd

from utils import coefficient_of_variation


class StatisticsEngine:
    def __init__(self, strategies):
        self.strategies = strategies

    def describe_metric(self, df, metric):
        s = df[metric].dropna()

        if len(s) == 0:
            return {}

        return {
            "Mean": s.mean(),
            "Median": s.median(),
            "Std": s.std(),
            "Variance": s.var(),
            "Minimum": s.min(),
            "Maximum": s.max(),
            "Q1": s.quantile(0.25),
            "Q3": s.quantile(0.75),
            "IQR": s.quantile(0.75) - s.quantile(0.25),
            "CV": coefficient_of_variation(s),
        }

    def strategy_statistics(self):
        rows = []

        for strategy, df in self.strategies.items():
            row = {"Strategy": strategy, "Stocks": len(df)}

            for col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    continue

                stats = self.describe_metric(df, col)

                for k, v in stats.items():
                    row[f"{col}_{k}"] = v

            rows.append(row)

        return pd.DataFrame(rows)
