"""
============================================================
Institutional Strategy Comparison Engine V3
File : recommendation/thresholds.py

Recommendation Thresholds

Author : Pavan Sai
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationThreshold:
    """
    Represents one recommendation threshold.
    """

    minimum_score: float
    label: str
    color: str


class RecommendationThresholds:
    """
    Institutional Recommendation Thresholds.

    Ordered from highest to lowest.
    """

    LEVELS = [
        RecommendationThreshold(90.0, "STRONG BUY", "#008000"),
        RecommendationThreshold(80.0, "BUY", "#32CD32"),
        RecommendationThreshold(70.0, "ACCUMULATE", "#00BFFF"),
        RecommendationThreshold(60.0, "WATCH", "#FFD700"),
        RecommendationThreshold(50.0, "HOLD", "#FFA500"),
        RecommendationThreshold(40.0, "REDUCE", "#FF8C00"),
        RecommendationThreshold(30.0, "SELL", "#FF4500"),
        RecommendationThreshold(0.0, "AVOID", "#DC143C"),
    ]

    @classmethod
    def get_label(cls, score: float) -> str:
        """
        Returns recommendation label.
        """

        for level in cls.LEVELS:
            if score >= level.minimum_score:
                return level.label

        return "UNKNOWN"

    @classmethod
    def get_color(cls, score: float) -> str:
        """
        Returns display color.
        """

        for level in cls.LEVELS:
            if score >= level.minimum_score:
                return level.color

        return "#808080"

    @classmethod
    def as_dataframe(cls):
        import pandas as pd

        return pd.DataFrame(
            {
                "Minimum Score": [level.minimum_score for level in cls.LEVELS],
                "Recommendation": [level.label for level in cls.LEVELS],
                "Color": [level.color for level in cls.LEVELS],
            }
        )


if __name__ == "__main__":
    print(RecommendationThresholds.as_dataframe())
