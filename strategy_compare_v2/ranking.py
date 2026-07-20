import pandas as pd

from config import WEIGHTS
from config import GRADE_RULES
from config import RECOMMENDATION_RULES

from utils import normalize


class RankingEngine:
    def __init__(self, statistics):
        self.statistics = statistics.copy()

    def calculate_scores(self):
        score = pd.Series(0.0, index=self.statistics.index)

        for metric, weight in WEIGHTS.items():
            column = f"{metric}_Mean"

            if column not in self.statistics.columns:
                continue

            values = normalize(self.statistics[column])

            score += values * weight

        self.statistics["Overall Score"] = score

        return self.statistics

    def assign_grade(self):
        grades = []

        for score in self.statistics["Overall Score"]:
            grade = "F"

            for threshold, value in sorted(GRADE_RULES.items(), reverse=True):
                if score >= threshold:
                    grade = value

                    break

            grades.append(grade)

        self.statistics["Grade"] = grades

        return self.statistics

    def assign_recommendation(self):
        recs = []

        for score in self.statistics["Overall Score"]:
            rec = "Reject"

            for threshold, value in sorted(RECOMMENDATION_RULES.items(), reverse=True):
                if score >= threshold:
                    rec = value

                    break

            recs.append(rec)

        self.statistics["Recommendation"] = recs

        return self.statistics

    def rank(self):
        self.statistics = self.statistics.sort_values("Overall Score", ascending=False)

        self.statistics.reset_index(drop=True, inplace=True)

        self.statistics.insert(0, "Rank", range(1, len(self.statistics) + 1))

        return self.statistics
