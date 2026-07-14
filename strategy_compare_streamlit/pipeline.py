from loader import StrategyLoader

from analyzer import StatisticsEngine

from ranking import RankingEngine

from recommendation import RecommendationEngine

from overlap import OverlapEngine

from excel_export import ExcelExporter


class StrategyPipeline:

    def __init__(

        self,

        input_folder

    ):

        self.input_folder = input_folder

    def execute(self):

        print("=" * 70)

        print("STRATEGY PIPELINE")

        print("=" * 70)

        loader = StrategyLoader(

            self.input_folder

        )

        strategies = loader.load()

        print(

            f"Reports Loaded : {len(strategies)}"

        )

        for name, df in strategies.items():

            print(

                f"{name:<45} {df.shape}"

            )

        analyzer = StatisticsEngine(

            strategies

        )

        statistics = analyzer.strategy_statistics()

        print()

        print(

            "Statistics Shape :",

            statistics.shape

        )

        ranking = RankingEngine(

            statistics

        )

        ranking.calculate_scores()

        ranking.assign_grade()

        ranking.assign_recommendation()

        ranked = ranking.rank()

        print(

            "Ranking Shape    :",

            ranked.shape

        )

        recommendation = RecommendationEngine(

            ranked

        )

        recommendations = recommendation.generate()

        print(

            "Recommendations  :",

            recommendations.shape

        )

        overlap = OverlapEngine(

            strategies

        )

        overlap_table = overlap.generate()

        print(

            "Overlap Shape    :",

            overlap_table.shape

        )

        exporter = ExcelExporter()

        report = exporter.export(

            ranked,

            recommendations,

            overlap_table

        )

        print(

            "Excel Report     :",

            report

        )

        print("=" * 70)

        print("PIPELINE COMPLETE")

        print("=" * 70)

        return {

            "strategies": strategies,

            "ranked": ranked,

            "recommendations": recommendations,

            "overlap": overlap_table,

            "excel": report

        }