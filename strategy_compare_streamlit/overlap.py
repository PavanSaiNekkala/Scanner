"""
Top Stock Overlap Engine
"""

import pandas as pd


###########################################################################
# OVERLAP ENGINE
###########################################################################

class OverlapEngine:

    def __init__(

        self,

        strategies,

        top_n=10

    ):

        self.strategies = strategies

        self.top_n = top_n

    ###########################################################################
    # BUILD OVERLAP TABLE
    ###########################################################################

    def generate(self):

        overlap = {}

        for strategy, dataframe in self.strategies.items():

            overlap[strategy] = self.top_stocks(

                dataframe

            )

        return pd.DataFrame(

            overlap

        )

    ###########################################################################
    # TOP STOCKS
    ###########################################################################

    def top_stocks(

        self,

        dataframe

    ):

        if "Stock" not in dataframe.columns:

            return []

        if "Overall Score" not in dataframe.columns:

            return []

        top = dataframe.nlargest(

            self.top_n,

            "Overall Score"

        )

        return top[

            "Stock"

        ].tolist()

    ###########################################################################
    # OVERLAP MATRIX
    ###########################################################################

    def overlap_matrix(self):

        names = list(

            self.strategies.keys()

        )

        matrix = pd.DataFrame(

            index=names,

            columns=names,

            dtype=int

        )

        cache = {}

        for name in names:

            cache[name] = set(

                self.top_stocks(

                    self.strategies[name]

                )

            )

        for left in names:

            for right in names:

                matrix.loc[

                    left,

                    right

                ] = len(

                    cache[left].intersection(

                        cache[right]

                    )

                )

        return matrix

    ###########################################################################
    # UNIQUE STOCKS
    ###########################################################################

    def unique_stocks(self):

        stocks = set()

        for dataframe in self.strategies.values():

            if "Stock" not in dataframe.columns:

                continue

            stocks.update(

                dataframe["Stock"]

                .dropna()

                .tolist()

            )

        return sorted(

            stocks

        )

    ###########################################################################
    # COMMON STOCKS
    ###########################################################################

    def common_stocks(self):

        names = list(

            self.strategies.keys()

        )

        if len(names) == 0:

            return []

        common = None

        for dataframe in self.strategies.values():

            if "Stock" not in dataframe.columns:

                continue

            current = set(

                dataframe["Stock"]

                .dropna()

            )

            if common is None:

                common = current

            else:

                common = common.intersection(

                    current

                )

        if common is None:

            return []

        return sorted(

            common

        )

    ###########################################################################
    # STOCK FREQUENCY
    ###########################################################################

    def frequency(self):

        frequency = {}

        for dataframe in self.strategies.values():

            if "Stock" not in dataframe.columns:

                continue

            for stock in dataframe["Stock"].dropna():

                frequency[stock] = (

                    frequency.get(

                        stock,

                        0

                    ) + 1

                )

        result = pd.DataFrame({

            "Stock":

                list(

                    frequency.keys()

                ),

            "Frequency":

                list(

                    frequency.values()

                )

        })

        return result.sort_values(

            "Frequency",

            ascending=False

        )

    ###########################################################################
    # SUMMARY
    ###########################################################################

    def summary(self):

        return {

            "Strategies": len(

                self.strategies

            ),

            "Unique Stocks": len(

                self.unique_stocks()

            ),

            "Common Stocks": len(

                self.common_stocks()

            )

        }