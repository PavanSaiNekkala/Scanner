from loader import StrategyLoader

from strategy_compare_v2.analyzer_v2 import StatisticsEngine

from ranking import RankingEngine

from dashboard import DashboardBuilder

from reasons import ReasonGenerator

from excel_writer import ExcelWriterEngine

from dashboard_excel import DashboardSheet

from charts import ChartBuilder

from insights import InsightEngine


def main():
    print("=" * 60)

    print("Strategy Comparison Engine V2")

    print("=" * 60)

    loader = StrategyLoader()

    strategies = loader.load()

    for name, df in strategies.items():
        print("=" * 60)
        print(name)
        print(df.columns.tolist())

    analyzer = StatisticsEngine(strategies)

    stats = analyzer.strategy_statistics()

    ranking = RankingEngine(stats)

    ranking.calculate_scores()

    ranking.assign_grade()

    ranking.assign_recommendation()

    ranked = ranking.rank()

    dashboard = DashboardBuilder(ranked)

    summary = dashboard.executive_summary()

    winners = dashboard.metric_winners()

    distribution = dashboard.recommendation_distribution()

    score_breakdown = dashboard.score_breakdown()

    overlap = dashboard.top10_overlap(strategies)

    reasons = ReasonGenerator(ranked, strategies).generate()

    insight = InsightEngine(ranked)

    executive = insight.executive_summary()

    leaders = insight.metric_leaders()

    deployment = insight.deployment()

    # -------------------------------------------------------
    # Create Workbook
    # -------------------------------------------------------

    excel = ExcelWriterEngine()

    excel.open()

    # -------------------------------------------------------
    # Write Sheets
    # -------------------------------------------------------

    excel.write_sheet(executive, "Executive Insights")

    excel.write_sheet(leaders, "Metric Leaders")

    excel.write_sheet(deployment, "Deployment Guide")

    excel.write_sheet(summary, "Executive Summary")

    excel.write_sheet(ranked, "Strategy Ranking")

    excel.write_sheet(winners, "Metric Winners")

    excel.write_sheet(score_breakdown, "Score Breakdown")

    excel.write_sheet(distribution, "Recommendations")

    excel.write_sheet(reasons, "Strengths & Weaknesses")

    excel.write_sheet(overlap, "Top 10 Stocks")

    print("=" * 60)
    print("DataFrame Shapes")
    print("=" * 60)

    print("Executive:", executive.shape)
    print("Leaders:", leaders.shape)
    print("Deployment:", deployment.shape)
    print("Summary:", summary.shape)
    print("Ranked:", ranked.shape)
    print("Winners:", winners.shape)
    print("Score Breakdown:", score_breakdown.shape)
    print("Distribution:", distribution.shape)
    print("Reasons:", reasons.shape)
    print("Overlap:", overlap.shape)

    # -------------------------------------------------------
    # Create Dashboard
    # -------------------------------------------------------

    dashboard_sheet = DashboardSheet(excel.writer)

    dashboard_sheet.create(ranked)

    # -------------------------------------------------------
    # Charts
    # -------------------------------------------------------

    charts = ChartBuilder(excel.writer)

    charts.build()

    # -------------------------------------------------------
    # Save Workbook
    # -------------------------------------------------------

    excel.save()


if __name__ == "__main__":
    main()
