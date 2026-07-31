from __future__ import annotations

from pathlib import Path

import pandas as pd
import datetime as dt

from scanner_monitor.services.workflow_service import WorkflowService
from scanner_monitor.universe_loader import (
    get_buckets_and_sectors,
)

# ==========================================================
# Load Universe
# ==========================================================

universe = pd.read_csv(
    "scanner_monitor/backtest/data/ind_nifty500list.csv" 
    #"scanner_monitor/backtest/data/universe.csv"
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

    start_date=dt.date(2018, 1, 1),

    end_date=dt.date.today() + dt.timedelta(days=1),

    sector_map=sector_map,
)

# ==========================================================
# Report Directories
# ==========================================================

latest_dir = Path(
    "scanner_monitor/reports/latest"
)

history_dir = Path(
    "scanner_monitor/reports/history"
)

# ==========================================================
# Workflow Summary
# ==========================================================

print(
    "\n=============================="
)

print(
    "WORKFLOW COMPLETED"
)

print(
    "=============================="
)

print(
    f"Status   : {result.statistics.status}"
)

print(
    f"Duration : {result.statistics.total_duration:.2f} seconds"
)

# ==========================================================
# Risk Violations
# ==========================================================

risk = result.risk

print(
    "\nRISK VIOLATIONS"
)

print(
    "---------------"
)

if risk.violations.empty:

    print(
        "No risk violations detected."
    )

else:

    total = len(
        risk.violations
    )

    critical = 0

    if "severity" in risk.violations.columns:

        critical = int(
            (
                risk.violations["severity"]
                .astype(str)
                .str.upper()
                == "CRITICAL"
            ).sum()
        )

    print(
        f"Detected {total} total risk violation(s), "
        f"{critical} critical.\n"
    )

    columns = [
        column
        for column in [
            "ticker",
            "rule",
            "severity",
            "value",
            "limit",
            "message",
        ]
        if column in risk.violations.columns
    ]

    if columns:

        print(
            risk.violations[columns]
            .to_string(index=False)
        )

    else:

        print(
            risk.violations.to_string(
                index=False,
            )
        )

# ==========================================================
# Latest Reports
# ==========================================================

print(
    "\nLATEST REPORTS"
)

print(
    "--------------"
)

if latest_dir.exists():

    latest_files = sorted(
        file
        for file in latest_dir.iterdir()
        if file.is_file()
    )

    if latest_files:

        for file in latest_files:

            print(
                f"✓ {file.name}"
            )

    else:

        print(
            "No latest reports found."
        )

else:

    print(
        "Latest report directory not found."
    )

# ==========================================================
# History Files
# ==========================================================

print(
    "\nHISTORY FILES"
)

print(
    "-------------"
)

if history_dir.exists():

    history_files = sorted(
        file
        for file in history_dir.iterdir()
        if file.is_file()
    )

    if history_files:

        for file in history_files:

            print(
                f"✓ {file.name}"
            )

    else:

        print(
            "No history files found."
        )

else:

    print(
        "History directory not found."
    )

# ==========================================================
# Output Locations
# ==========================================================

print(
    "\nREPORT DIRECTORIES"
)

print(
    "------------------"
)

print(
    f"Latest  : {latest_dir}"
)

print(
    f"History : {history_dir}"
)

print(
    "\n==============================\n"
)
