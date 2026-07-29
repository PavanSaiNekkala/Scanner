from __future__ import annotations

import pandas as pd

from scanner_monitor.services.workflow_service import WorkflowService

from scanner_monitor.universe_loader import (
    get_buckets_and_sectors,
)

# ==========================================================
# Load Universe
# ==========================================================

universe = pd.read_csv(
    "scanner_monitor/backtest/data/universe.csv"
)

_, sector_map, _ = get_buckets_and_sectors()

print(
    f"Loaded {len(sector_map)} sector mappings."
)

# ==========================================================
# Initialize Workflow
# ==========================================================

workflow = WorkflowService()


# ==========================================================
# Execute Pipeline
# ==========================================================

result = workflow.run(

    tickers=universe["Symbol"].tolist(),

    strategy="PASS_combined",

    params={
        "regime": 15.0,
        "atr": 2.0,
        "roc": 10.0,
        "volr": 1.5,
        "rsi_os": 30,
    },

    bt_kwargs={
        "target_pct": 10,
        "stop_value": 2,
        "max_stop_pct": 8,
        "max_hold": 60,
        "stop_method": "ATR",
    },

    start_date="2018-01-01",

    end_date="2026-07-01",

    sector_map=sector_map,
)


# ==========================================================
# Execution Summary
# ==========================================================

print(
    "\n=============================="
)

print(
    "WORKFLOW COMPLETED"
)

print(
    "STATUS:",
    result.statistics.status,
)

print(
    "DURATION:",
    result.statistics.total_duration,
)


# ==========================================================
# Reports
# ==========================================================

if result.report:

    print(
        "\nREPORTS GENERATED:"
    )

    for file in result.report.exported_files:

        print(
            file
        )


print(
    "==============================\n"
)