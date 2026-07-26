import pandas as pd
from pathlib import Path

from services.workflow_service import WorkflowService

# Load your universe
universe = pd.read_csv("backtest/data/universe.csv")

workflow = WorkflowService()

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

    end_date="2026-01-01",
)


output_dir = Path("reports")

output_dir.mkdir(
    exist_ok=True
)

# Portfolio
result.portfolio.portfolio.to_csv(
    output_dir / "portfolio.csv",
    index=False,
)


# Orders
result.execution.orders.to_csv(
    output_dir / "execution_orders.csv",
    index=False,
)


# Risk
if hasattr(result.risk, "metrics"):

    pd.DataFrame(
        result.risk.metrics
    ).to_csv(
        output_dir / "risk_metrics.csv",
        index=False,
    )


print(
    "Outputs saved:",
    output_dir.resolve()
)

print(result.statistics.status)
print(result.statistics.total_duration)