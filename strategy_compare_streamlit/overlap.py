"""
Top Stock Overlap Engine
"""

import pandas as pd

from config import TOP_N, DECIMAL_PLACES

###########################################################################
# OVERLAP ENGINE
###########################################################################


class OverlapEngine:
    def __init__(self, strategies, top_n=TOP_N):
        self.strategies = strategies

        self.top_n = top_n

        self._top_cache = {}

    ###########################################################################
    # BUILD TOP STOCK TABLE
    ###########################################################################

    def generate(self):
        overlap = {}

        for strategy, dataframe in self.strategies.items():
            overlap[strategy] = self.top_stocks(dataframe)

        return pd.DataFrame(overlap)

    ###########################################################################
    # TOP STOCKS
    ###########################################################################

    def top_stocks(self, dataframe):
        cache_key = id(dataframe)

        if cache_key in self._top_cache:
            return self._top_cache[cache_key]

        if dataframe.empty:
            return []

        if "Stock" not in dataframe.columns:
            return []

        if "Overall Score" not in dataframe.columns:
            return []

        top = dataframe.sort_values("Overall Score", ascending=False).head(self.top_n)

        stocks = top["Stock"].dropna().astype(str).str.strip().tolist()

        self._top_cache[cache_key] = stocks

        return stocks

    ###########################################################################
    # OVERLAP MATRIX
    ###########################################################################

    def overlap_matrix(self):
        names = list(self.strategies.keys())

        matrix = pd.DataFrame(0, index=names, columns=names, dtype=int)

        cache = {}

        for strategy in names:
            cache[strategy] = set(self.top_stocks(self.strategies[strategy]))

        for left in names:
            for right in names:
                matrix.loc[left, right] = len(cache[left].intersection(cache[right]))

        return matrix

    ###########################################################################
    # OVERLAP PERCENTAGE
    ###########################################################################

    def overlap_percentage(self):
        names = list(self.strategies.keys())

        matrix = pd.DataFrame(0.0, index=names, columns=names, dtype=float)

        cache = {}

        for strategy in names:
            cache[strategy] = set(self.top_stocks(self.strategies[strategy]))

        for left in names:
            for right in names:
                left_size = len(cache[left])

                if left_size == 0:
                    percentage = 0

                else:
                    percentage = (
                        len(cache[left].intersection(cache[right])) / left_size
                    ) * 100

                matrix.loc[left, right] = round(percentage, DECIMAL_PLACES)

        return matrix

    ###########################################################################
    # JACCARD SIMILARITY
    ###########################################################################

    def jaccard_similarity(self):
        names = list(self.strategies.keys())

        matrix = pd.DataFrame(0.0, index=names, columns=names, dtype=float)

        cache = {}

        for strategy in names:
            cache[strategy] = set(self.top_stocks(self.strategies[strategy]))

        for left in names:
            for right in names:
                intersection = len(cache[left].intersection(cache[right]))

                union = len(cache[left].union(cache[right]))

                similarity = 0

                if union > 0:
                    similarity = (intersection / union) * 100

                matrix.loc[left, right] = round(similarity, DECIMAL_PLACES)

        return matrix

    ###########################################################################
    # UNIQUE STOCKS
    ###########################################################################

    def unique_stocks(self):
        stocks = set()

        for dataframe in self.strategies.values():
            if "Stock" not in dataframe.columns:
                continue

            stocks.update(dataframe["Stock"].dropna().astype(str).str.strip().tolist())

        return sorted(stocks)

    ###########################################################################
    # COMMON STOCKS
    ###########################################################################

    def common_stocks(self):
        common = None

        for dataframe in self.strategies.values():
            if "Stock" not in dataframe.columns:
                continue

            current = set(dataframe["Stock"].dropna().astype(str).str.strip())

            if common is None:
                common = current

            else:
                common = common.intersection(current)

        if common is None:
            return []

        return sorted(common)

    ###########################################################################
    # STOCK FREQUENCY
    ###########################################################################

    def frequency(self):
        frequency = {}

        for dataframe in self.strategies.values():
            if "Stock" not in dataframe.columns:
                continue

            for stock in dataframe["Stock"].dropna().astype(str).str.strip():
                frequency[stock] = frequency.get(stock, 0) + 1

        result = pd.DataFrame(
            {"Stock": list(frequency.keys()), "Frequency": list(frequency.values())}
        )

        return result.sort_values("Frequency", ascending=False, ignore_index=True)

    ###########################################################################
    # STRATEGY SIMILARITY
    ###########################################################################

    def strategy_similarity(self):
        similarity = self.jaccard_similarity()

        if similarity.empty:
            return pd.DataFrame()

        rows = []

        names = list(similarity.index)

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                rows.append(
                    {
                        "Strategy A": names[i],
                        "Strategy B": names[j],
                        "Similarity (%)": round(
                            similarity.loc[names[i], names[j]], DECIMAL_PLACES
                        ),
                    }
                )

        dataframe = pd.DataFrame(rows)

        if dataframe.empty:
            return dataframe

        return dataframe.sort_values(
            "Similarity (%)", ascending=False, ignore_index=True
        )

    ###########################################################################
    # EXECUTIVE SUMMARY
    ###########################################################################

    def executive_summary(self):
        similarity = self.strategy_similarity()

        frequency = self.frequency()

        return {
            "Strategies": len(self.strategies),
            "Top N": self.top_n,
            "Unique Stocks": len(self.unique_stocks()),
            "Common Stocks": len(self.common_stocks()),
            "Most Frequent Stock": (
                frequency.iloc[0]["Stock"] if not frequency.empty else None
            ),
            "Highest Frequency": (
                int(frequency.iloc[0]["Frequency"]) if not frequency.empty else 0
            ),
            "Most Similar Pair": (
                (
                    f"{similarity.iloc[0]['Strategy A']} ↔ "
                    f"{similarity.iloc[0]['Strategy B']}"
                )
                if not similarity.empty
                else None
            ),
            "Highest Similarity (%)": (
                round(similarity.iloc[0]["Similarity (%)"], DECIMAL_PLACES)
                if not similarity.empty
                else 0
            ),
        }

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):
        return {
            "Strategies": len(self.strategies),
            "Unique Stocks": len(self.unique_stocks()),
            "Common Stocks": len(self.common_stocks()),
        }

    ###########################################################################
    # COMPLETE REPORT
    ###########################################################################

    def report(self):
        return {
            "top_stocks": self.generate(),
            "overlap_matrix": self.overlap_matrix(),
            "overlap_percentage": self.overlap_percentage(),
            "jaccard_similarity": self.jaccard_similarity(),
            "strategy_similarity": self.strategy_similarity(),
            "frequency": self.frequency(),
            "unique_stocks": self.unique_stocks(),
            "common_stocks": self.common_stocks(),
            "executive_summary": self.executive_summary(),
            "summary": self.summary(),
        }
