"""
============================================================
Institutional Strategy Comparison Engine V3

File : feature_engineering/feature_engine.py

Production Grade Master Feature Engineering Engine

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

import time

from typing import Dict, Any

import pandas as pd

from core.cache import CacheManager
from core.logger import get_logger


from feature_engineering.reward_risk import RewardRiskEngine
from feature_engineering.expectancy import ExpectancyEngine
from feature_engineering.profitability import ProfitabilityEngine
from feature_engineering.efficiency import EfficiencyEngine
from feature_engineering.stability import StabilityEngine
from feature_engineering.quality import QualityEngine
from feature_engineering.opportunity import OpportunityEngine
from feature_engineering.institutional_metrics import (
    InstitutionalMetricsEngine
)


logger = get_logger(__name__)


class FeatureEngine:
    """
    Master Feature Engineering Pipeline.

    Executes feature engineering modules
    in dependency order.
    """


    def __init__(
        self,
        dataframe: pd.DataFrame,
        use_cache: bool = False,
    ):

        self.df = dataframe.copy()

        self.use_cache = use_cache

        self.cache = CacheManager()

        self.execution_time = 0.0

        self.feature_count = 0

        self.generated_features = []

        self.module_summary = []



    # ==================================================
    # COLUMN CONTRACT NORMALIZATION
    # ==================================================

    def _normalize_feature_columns(self):

        """
        Convert raw backtest columns into
        institutional feature contract.
        """

        created = []


        # --------------------------------------------------
        # Win Percentage
        # --------------------------------------------------

        if "outcome" in self.df.columns:

            if "Win_Pct" not in self.df.columns:

                self.df["Win_Pct"] = (

                    self.df["outcome"]
                    .astype(str)
                    .str.lower()
                    .eq("win")
                    .astype(int)
                    .mean()

                    * 100

                )

                created.append(
                    "Win_Pct"
                )


        # --------------------------------------------------
        # Average Win
        # --------------------------------------------------

        if "net_return_Pct" in self.df.columns:

            if "Avg_winPct" not in self.df.columns:

                wins = self.df.loc[

                    self.df["net_return_Pct"] > 0,

                    "net_return_Pct"

                ]


                self.df["Avg_winPct"] = (

                    wins.mean()

                    if not wins.empty

                    else 0

                )


                created.append(
                    "Avg_winPct"
                )



        # --------------------------------------------------
        # Average Loss
        # --------------------------------------------------

        if "net_return_Pct" in self.df.columns:

            if "Avg_lossPct" not in self.df.columns:


                losses = self.df.loc[

                    self.df["net_return_Pct"] < 0,

                    "net_return_Pct"

                ]


                self.df["Avg_lossPct"] = (

                    losses.abs().mean()

                    if not losses.empty

                    else 0

                )


                created.append(
                    "Avg_lossPct"
                )



        # --------------------------------------------------
        # Expectancy
        # --------------------------------------------------

        if {

            "Win_Pct",
            "Avg_winPct",
            "Avg_lossPct"

        }.issubset(self.df.columns):


            if "ExpectancyPct" not in self.df.columns:


                win_rate = (

                    self.df["Win_Pct"]

                    /

                    100

                )


                self.df["ExpectancyPct"] = (

                    win_rate

                    *

                    self.df["Avg_winPct"]

                    -

                    (1-win_rate)

                    *

                    self.df["Avg_lossPct"]

                )


                created.append(
                    "ExpectancyPct"
                )


            
        if "Trades" not in self.df.columns:

            self.df["Trades"] = 1


        # --------------------------------------------------
        # Profit Factor
        # --------------------------------------------------

        if "net_return_Pct" in self.df.columns:


            if "Profit_Factor" not in self.df.columns:


                gross_profit = self.df.loc[

                    self.df["net_return_Pct"] > 0,

                    "net_return_Pct"

                ].sum()


                gross_loss = abs(

                    self.df.loc[

                        self.df["net_return_Pct"] < 0,

                        "net_return_Pct"

                    ].sum()

                )


                self.df["Profit_Factor"] = (

                    gross_profit / gross_loss

                    if gross_loss != 0

                    else 0

                )


                created.append(
                    "Profit_Factor"
                )



        logger.info(

            "Created feature aliases: %s",

            created

        )


        return self.df

    # ==================================================
    # DEBUG INPUT CONTRACT
    # ==================================================

    def _validate_feature_inputs(self):

        required_watch = [

            "Avg win%",

            "Avg loss%",

            "Win %",

            "Expectancy%",

            "Profit Factor",

            "Target %",

            "Stop %"

        ]


        available = [

            col

            for col in required_watch

            if col in self.df.columns

        ]


        missing = [

            col

            for col in required_watch

            if col not in self.df.columns

        ]


        logger.info(
            "Feature Engine available columns: %s",
            available
        )


        if missing:

            logger.warning(
                "Feature Engine missing columns: %s",
                missing
            )



    # ==================================================
    # TRACK FEATURES
    # ==================================================

    def _track_features(
        self,
        before,
        after
    ):


        generated = sorted(

            list(

                set(after)

                -

                set(before)

            )

        )


        self.generated_features.extend(
            generated
        )


        return generated



    # ==================================================
    # MODULE PIPELINE
    # ==================================================

    def _modules(self):

        return [

            RewardRiskEngine,

            ExpectancyEngine,

            ProfitabilityEngine,

            EfficiencyEngine,

            StabilityEngine,

            QualityEngine,

            OpportunityEngine,

            InstitutionalMetricsEngine,

        ]



    # ==================================================
    # RUN ENGINE
    # ==================================================

    def run(self):


        logger.info("=" * 80)

        logger.info(
            "Starting Feature Engineering..."
        )


        start = time.perf_counter()



        # Normalize columns

        self._normalize_feature_columns()


        self._validate_feature_inputs()



        # Execute modules

        for module in self._modules():


            module_start = time.perf_counter()


            module_name = module.__name__



            logger.info(
                "Running %s",
                module_name
            )


            before = (
                self.df.columns.tolist()
            )



            try:


                engine = module(
                    self.df
                )


                self.df = engine.generate()



                after = (
                    self.df.columns.tolist()
                )



                new_features = self._track_features(

                    before,

                    after

                )



                elapsed = round(

                    time.perf_counter()

                    -

                    module_start,

                    4

                )



                self.module_summary.append({

                    "Module":
                        module_name,

                    "Status":
                        "Completed",

                    "Generated":
                        new_features,

                    "Count":
                        len(new_features),

                    "Time":
                        elapsed

                })



                if new_features:

                    logger.info(

                        "%s generated %d features",

                        module_name,

                        len(new_features)

                    )


                else:

                    logger.warning(

                        "%s generated no features",

                        module_name

                    )



            except Exception as error:


                logger.exception(

                    "%s failed : %s",

                    module_name,

                    error

                )


                self.module_summary.append({

                    "Module":
                        module_name,

                    "Status":
                        "Failed",

                    "Error":
                        str(error)

                })



        # Remove duplicate tracking

        self.generated_features = sorted(

            set(

                self.generated_features

            )

        )


        self.feature_count = len(

            self.generated_features

        )



        self.execution_time = round(

            time.perf_counter()

            -

            start,

            3

        )



        logger.info(

            "Generated %d engineered features.",

            self.feature_count

        )


        logger.info(

            "Feature Engineering completed in %.3f seconds.",

            self.execution_time

        )


        logger.info("=" * 80)



        return self.df



    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self) -> Dict[str, Any]:

        return {


            "Execution Time":

                self.execution_time,


            "Generated Features":

                self.feature_count,


            "Feature Names":

                self.generated_features,


            "Module Summary":

                self.module_summary

        }



    # ==================================================
    # DATAFRAME ACCESS
    # ==================================================

    def get_dataframe(self):

        return self.df



if __name__ == "__main__":

    print(
        "Import FeatureEngine into main.py"
    )