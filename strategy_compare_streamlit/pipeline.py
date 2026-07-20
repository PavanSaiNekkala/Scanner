"""
Strategy Comparison Pipeline
"""

from loader import StrategyLoader

from validator import StrategyValidator

from analyzer import StatisticsEngine

from strategy_compare_streamlit.ranking_engine import RankingEngine

from recommendation import RecommendationEngine

from overlap import OverlapEngine

from insights import InsightEngine

from charts import ChartEngine

from excel_export import ExcelExporter

from logger import StrategyLogger

###########################################################################
# PIPELINE
###########################################################################


class StrategyPipeline:
    def __init__(self, input_folder):
        self.input_folder = input_folder

        self.logger = StrategyLogger()

        self.validator = StrategyValidator(input_folder)

        self.loader = StrategyLoader(input_folder)

        self.exporter = ExcelExporter()

    ###########################################################################
    # INITIALIZE
    ###########################################################################

    def initialize(self):
        self.logger.separator()

        self.logger.start("Strategy Pipeline")

        print("=" * 80)

        print("INSTITUTIONAL STRATEGY COMPARISON PIPELINE")

        print("=" * 80)

        print(f"Input Folder : {self.input_folder}")

        print()

    ###########################################################################
    # VALIDATE INPUT
    ###########################################################################

    def validate(self):
        print("Validating Reports...")

        errors = self.validator.validate()

        if errors:
            print()

            print("Validation Failed")

            print("-" * 80)

            for error in errors:
                print(error)

            self.logger.error("Validation Failed")

            raise ValueError("\n".join(errors))

        print("Validation Passed")

        self.logger.info("Validation Passed")

        print()

    ###########################################################################
    # LOAD REPORTS
    ###########################################################################

    def load_reports(self):
        print("Loading Strategy Reports...")

        strategies = self.loader.load()

        print(f"Reports Loaded : {len(strategies)}")

        for name, dataframe in strategies.items():
            print(f"{name:<45} {dataframe.shape}")

        self.logger.info(f"{len(strategies)} reports loaded.")

        print()

        return strategies

    ###########################################################################
    # ANALYZE REPORTS
    ###########################################################################

    def analyze(self, strategies):
        print("Generating Statistics...")

        analyzer = StatisticsEngine(strategies)

        statistics = analyzer.strategy_statistics()

        statistics_report = analyzer.report()

        print("Statistics Shape :", statistics.shape)

        print("Metric Leaders   :", len(analyzer.metric_leaders()))

        print("Data Quality     :", analyzer.data_quality().shape)

        self.logger.info("Statistics generated.")

        print()

        return {
            "engine": analyzer,
            "statistics": statistics,
            "report": statistics_report,
            "leaders": analyzer.metric_leaders(),
            "quality": analyzer.data_quality(),
        }

    ###########################################################################
    # RANK STRATEGIES
    ###########################################################################

    def rank(self, statistics):
        print("Ranking Strategies...")

        ranking = RankingEngine(statistics)

        ranking.calculate_scores()

        ranking.assign_grade()

        ranking.assign_recommendation()

        ranked = ranking.rank()

        print("Ranking Shape    :", ranked.shape)

        print("Top Strategy     :", ranked.iloc[0]["Strategy"])

        print("Best Score       :", round(ranked.iloc[0]["Overall Score"], 2))

        self.logger.info("Ranking completed.")

        print()

        return {"engine": ranking, "ranked": ranked, "summary": ranking.summary()}

    ###########################################################################
    # RECOMMENDATION ENGINE
    ###########################################################################

    def recommend(self, ranked):
        print("Generating Recommendations...")

        recommendation = RecommendationEngine(ranked)

        recommendations = recommendation.generate()

        print("Recommendations  :", recommendations.shape)

        self.logger.info("Recommendations generated.")

        print()

        return {
            "engine": recommendation,
            "data": recommendations,
            "summary": recommendation.executive_summary(),
            "deployment": recommendation.deployment_guide(),
        }

    ###########################################################################
    # OVERLAP ANALYSIS
    ###########################################################################

    def overlap(self, strategies):
        print("Analyzing Stock Overlap...")

        overlap = OverlapEngine(strategies)

        overlap_table = overlap.generate()

        print("Overlap Shape    :", overlap_table.shape)

        self.logger.info("Overlap analysis completed.")

        print()

        return {
            "engine": overlap,
            "table": overlap_table,
            "matrix": overlap.overlap_matrix(),
            "percentage": overlap.overlap_percentage(),
            "similarity": overlap.jaccard_similarity(),
            "frequency": overlap.frequency(),
            "summary": overlap.executive_summary(),
        }

    ###########################################################################
    # INSIGHTS
    ###########################################################################

    def insights(self, ranked):
        print("Generating Executive Insights...")

        insight = InsightEngine(ranked)

        report = insight.report()

        print("Executive Insights Ready")

        self.logger.info("Insight report generated.")

        print()

        return {"engine": insight, "report": report}

    ###########################################################################
    # CHARTS
    ###########################################################################

    def charts(self, ranked):
        print("Building Charts...")

        charts = ChartEngine(ranked)

        report = charts.report()

        print("Charts Generated")

        self.logger.info("Charts generated.")

        print()

        return {"engine": charts, "report": report}

    ###########################################################################
    # EXECUTE PIPELINE
    ###########################################################################

    def execute(self):
        try:
            ###################################################################
            # INITIALIZATION
            ###################################################################

            self.initialize()

            self.validate()

            ###################################################################
            # LOAD
            ###################################################################

            strategies = self.load_reports()

            ###################################################################
            # ANALYSIS
            ###################################################################

            analysis = self.analyze(strategies)

            ###################################################################
            # RANKING
            ###################################################################

            ranking = self.rank(analysis["statistics"])

            ###################################################################
            # RECOMMENDATIONS
            ###################################################################

            recommendations = self.recommend(ranking["ranked"])

            ###################################################################
            # OVERLAP
            ###################################################################

            overlap = self.overlap(strategies)

            ###################################################################
            # INSIGHTS
            ###################################################################

            insights = self.insights(ranking["ranked"])

            ###################################################################
            # CHARTS
            ###################################################################

            charts = self.charts(ranking["ranked"])

            ###################################################################
            # EXPORT
            ###################################################################

            print("Exporting Reports...")

            export = self.exporter.report(
                ranking["ranked"], recommendations["data"], overlap["table"]
            )

            self.logger.info("Excel report exported.")

            print()

            print("Workbook :", export["excel"])

            print()

            ###################################################################
            # FINISH
            ###################################################################

            self.logger.finish("Strategy Pipeline")

            self.logger.separator()

            print("=" * 80)

            print("PIPELINE COMPLETED SUCCESSFULLY")

            print("=" * 80)

            print()

            return {
                "strategies": strategies,
                "statistics": analysis["statistics"],
                "statistics_report": analysis["report"],
                "metric_leaders": analysis["leaders"],
                "data_quality": analysis["quality"],
                "ranked": ranking["ranked"],
                "ranking_summary": ranking["summary"],
                "recommendations": recommendations["data"],
                "recommendation_summary": recommendations["summary"],
                "deployment": recommendations["deployment"],
                "overlap": overlap["table"],
                "overlap_matrix": overlap["matrix"],
                "overlap_percentage": overlap["percentage"],
                "overlap_similarity": overlap["similarity"],
                "stock_frequency": overlap["frequency"],
                "overlap_summary": overlap["summary"],
                "insights": insights["report"],
                "charts": charts["report"],
                "excel": export["excel"],
                "exports": export,
            }

        except Exception as exception:
            self.logger.exception(str(exception))

            print()

            print("=" * 80)

            print("PIPELINE FAILED")

            print("=" * 80)

            print(exception)

            raise
