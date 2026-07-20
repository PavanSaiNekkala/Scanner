# Examples

## Institutional Strategy Comparison Platform V4

______________________________________________________________________

# Table of Contents

1. Introduction
1. Input Data Format
1. Basic Workflow
1. Complete Workflow
1. Portfolio Allocation Examples
1. Recommendation Examples
1. Report Generation
1. Batch Processing
1. Error Handling Examples
1. Best Practices

______________________________________________________________________

# 1. Introduction

This document demonstrates how to use the Institutional Strategy Comparison Platform through practical examples.

The examples cover the complete workflow, from loading backtest results to generating institutional reports.

______________________________________________________________________

# 2. Input Data Format

The platform expects strategy statistics in CSV or Excel format.

Example:

| Stock | Expectancy% | Profit Factor | Reward Risk | Trades / Year | Signal Quality | Holding Efficiency |
|---------|-------------|---------------|-------------|----------------|----------------|--------------------|
| RELIANCE | 4.52 | 2.31 | 2.05 | 118 | 86.4 | 79.2 |
| INFY | 3.87 | 2.11 | 1.92 | 94 | 82.1 | 74.6 |
| TCS | 5.13 | 2.78 | 2.34 | 132 | 89.6 | 83.5 |

______________________________________________________________________

# 3. Basic Workflow

## Step 1 — Load Data

```python
import pandas as pd

df = pd.read_csv("strategy_results.csv")
```

______________________________________________________________________

## Step 2 — Calculate Derived Metrics

```python
from derived_metrics import calculate_scores

df = calculate_scores(df)
```

Generated columns include:

- Edge Score
- Reliability Score
- Efficiency Score
- Composite Score

______________________________________________________________________

## Step 3 — Compare Strategies

```python
from comparison import compare_strategies

ranked = compare_strategies(df)
```

Example output:

| Rank | Stock | Composite Score |
|------|-------|-----------------|
| 1 | TCS | 94.7 |
| 2 | RELIANCE | 91.5 |
| 3 | INFY | 88.2 |

______________________________________________________________________

## Step 4 — Build Portfolio

```python
from portfolio import allocate_portfolio

portfolio = allocate_portfolio(
    ranked,
    method="composite"
)
```

Example:

| Stock | Weight |
|---------|--------|
| TCS | 34.6% |
| RELIANCE | 33.2% |
| INFY | 32.2% |

______________________________________________________________________

## Step 5 — Export Report

```python
from reports import export_excel

export_excel(
    portfolio,
    "portfolio_report.xlsx"
)
```

______________________________________________________________________

# 4. Complete Workflow

```python
import pandas as pd

from derived_metrics import calculate_scores
from comparison import compare_strategies
from portfolio import allocate_portfolio
from reports import export_excel

# Load data
df = pd.read_csv("strategy_results.csv")

# Calculate institutional metrics
df = calculate_scores(df)

# Compare strategies
ranked = compare_strategies(df)

# Build portfolio
portfolio = allocate_portfolio(
    ranked,
    method="composite"
)

# Export workbook
export_excel(
    portfolio,
    "institutional_report.xlsx"
)
```

______________________________________________________________________

# 5. Portfolio Allocation Examples

## Equal Weight

```python
portfolio = allocate_portfolio(
    ranked,
    method="equal"
)
```

Output:

| Stock | Weight |
|---------|--------|
| A | 20% |
| B | 20% |
| C | 20% |
| D | 20% |
| E | 20% |

______________________________________________________________________

## Composite Weight

```python
portfolio = allocate_portfolio(
    ranked,
    method="composite"
)
```

Output:

| Stock | Weight |
|---------|--------|
| A | 34.7% |
| B | 26.1% |
| C | 18.2% |
| D | 13.4% |
| E | 7.6% |

______________________________________________________________________

## Reliability Weight

```python
portfolio = allocate_portfolio(
    ranked,
    method="reliability"
)
```

Allocates more capital to statistically consistent strategies.

______________________________________________________________________

## Blended Weight

```python
portfolio = allocate_portfolio(
    ranked,
    method="blended"
)
```

Uses a weighted combination of Composite Score, Edge Score, and Reliability Score.

______________________________________________________________________

# 6. Recommendation Examples

Example output:

| Composite Score | Recommendation |
|-----------------|---------------|
| 95 | Strong Buy |
| 86 | Buy |
| 72 | Watch |
| 55 | Improve |
| 34 | Avoid |

These recommendations are configurable through the `config` package.

______________________________________________________________________

# 7. Report Generation

Generate an Excel workbook:

```python
export_excel(
    ranked,
    "strategy_report.xlsx"
)
```

Typical workbook:

```
strategy_report.xlsx

Summary
Rankings
Portfolio
Metrics
Charts
Configuration
```

______________________________________________________________________

Generate dashboard data:

```python
from reports import generate_dashboard

dashboard = generate_dashboard(ranked)
```

______________________________________________________________________

Generate summary statistics:

```python
from reports import summary_report

summary = summary_report(ranked)
```

Example:

```python
{
    "Strategies": 150,
    "Average Composite Score": 78.5,
    "Strong Buy": 12,
    "Buy": 28
}
```

______________________________________________________________________

# 8. Batch Processing

Process multiple strategy files:

```python
from pathlib import Path

for file in Path("input").glob("*.csv"):
    df = pd.read_csv(file)

    df = calculate_scores(df)

    ranked = compare_strategies(df)

    export_excel(
        ranked,
        f"output/{file.stem}.xlsx"
    )
```

______________________________________________________________________

# 9. Error Handling Examples

Handle missing files:

```python
try:
    df = pd.read_csv("strategy_results.csv")
except FileNotFoundError:
    print("Input file not found.")
```

Handle missing columns:

```python
required = [
    "Expectancy%",
    "Profit Factor",
    "Reward Risk"
]

missing = [
    col for col in required
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )
```

______________________________________________________________________

# 10. Best Practices

- Validate input data before processing.
- Keep configuration values centralized.
- Use vectorized pandas operations.
- Generate reports from ranked data rather than raw inputs.
- Re-run comparisons after modifying scoring weights.
- Version-control configuration and output templates.

______________________________________________________________________

# Typical Workflow

```
CSV / Excel
      │
      ▼
Load Data
      │
      ▼
Calculate Derived Metrics
      │
      ▼
Compare Strategies
      │
      ▼
Build Portfolio
      │
      ▼
Generate Reports
      │
      ▼
Excel / Dashboard
```

______________________________________________________________________

# Sample Project Structure

```
project/

input/
    strategy_results.csv

output/
    institutional_report.xlsx

config/
derived_metrics/
comparison/
portfolio/
reports/
tests/
docs/
```

______________________________________________________________________

# Summary

These examples demonstrate the standard workflow of the Institutional Strategy Comparison Platform. By following the sequence of loading data, calculating metrics, ranking strategies, constructing portfolios, and generating reports, users can produce consistent, reproducible, and institutional-grade analyses with minimal code.
