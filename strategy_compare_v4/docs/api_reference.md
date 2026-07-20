# API Reference

## Institutional Strategy Comparison Platform V4

**Version:** 1.0.0

______________________________________________________________________

# Table of Contents

1. Introduction
1. Package Overview
1. comparison Package
1. derived_metrics Package
1. portfolio Package
1. reports Package
1. config Package
1. utils Package
1. Main Application
1. Exceptions
1. Data Models
1. Return Types
1. Extension Guidelines

______________________________________________________________________

# 1. Introduction

This document describes the public API of the Institutional Strategy Comparison Platform.

Only documented public functions should be used by external modules.

Functions beginning with `_` are considered internal implementation details and may change without notice.

______________________________________________________________________

# 2. Package Overview

```
strategy_compare_v4/

comparison/
derived_metrics/
portfolio/
reports/
config/
utils/

strategy_comparison.py
backtest_statistics_generator.py
```

______________________________________________________________________

# 3. comparison Package

Responsible for comparing, ranking and analysing trading strategies.

______________________________________________________________________

## compare_strategies()

### Description

Ranks strategies using institutional metrics.

### Signature

```python
compare_strategies(
    df: pd.DataFrame
) -> pd.DataFrame
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| df | DataFrame | Input strategy metrics |

### Returns

Ranked DataFrame.

### Raises

- ValueError
- KeyError

______________________________________________________________________

## compare_stocks()

### Description

Compares multiple stocks across strategies.

### Signature

```python
compare_stocks(
    df: pd.DataFrame
) -> pd.DataFrame
```

Returns

Ranked stocks.

______________________________________________________________________

## strategy_leaderboard()

Returns the highest-ranked strategies.

```python
strategy_leaderboard(
    df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame
```

______________________________________________________________________

## stock_leaderboard()

Returns the highest-ranked stocks.

```python
stock_leaderboard(
    df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame
```

______________________________________________________________________

## robustness_score()

Calculates robustness metrics.

```python
robustness_score(
    df: pd.DataFrame
) -> pd.Series
```

______________________________________________________________________

## strategy_correlation()

Calculates the correlation matrix.

```python
strategy_correlation(
    df: pd.DataFrame
) -> pd.DataFrame
```

______________________________________________________________________

# 4. derived_metrics Package

Calculates institutional metrics.

______________________________________________________________________

## calculate_performance_metrics()

```python
calculate_performance_metrics(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces:

- Expectancy
- Profit Factor
- Reward Risk
- Profit Velocity

______________________________________________________________________

## calculate_risk_metrics()

```python
calculate_risk_metrics(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces:

- Risk Score
- Stability
- Drawdown Recovery

______________________________________________________________________

## calculate_exit_metrics()

```python
calculate_exit_metrics(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces:

- Winning Exit %
- Losing Exit %
- Target %
- Stop %
- Trail %

______________________________________________________________________

## calculate_opportunity_metrics()

```python
calculate_opportunity_metrics(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces:

- Signal Quality
- Holding Efficiency
- Opportunity Score

______________________________________________________________________

## calculate_scores()

```python
calculate_scores(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces

- Edge Score
- Reliability Score
- Efficiency Score
- Composite Score

______________________________________________________________________

# 5. portfolio Package

Responsible for portfolio construction.

______________________________________________________________________

## allocate_portfolio()

```python
allocate_portfolio(
    df: pd.DataFrame,
    method: str = "composite"
) -> pd.DataFrame
```

Supported methods

- equal
- composite
- edge
- reliability
- blended

Returns

Portfolio weights.

______________________________________________________________________

## apply_risk_filters()

```python
apply_risk_filters(
    df: pd.DataFrame
) -> pd.DataFrame
```

Removes strategies failing quality criteria.

______________________________________________________________________

## normalize_weights()

```python
normalize_weights(
    weights: pd.Series
) -> pd.Series
```

Guarantees total allocation equals 100%.

______________________________________________________________________

## portfolio_statistics()

```python
portfolio_statistics(
    df: pd.DataFrame
) -> dict
```

Returns

- Total Weight
- Average Expectancy
- Average Composite Score
- Holdings
- Concentration

______________________________________________________________________

# 6. reports Package

Produces reports and visualisations.

______________________________________________________________________

## export_excel()

```python
export_excel(
    df: pd.DataFrame,
    filename: str
) -> None
```

Exports complete workbook.

______________________________________________________________________

## generate_dashboard()

```python
generate_dashboard(
    df: pd.DataFrame
) -> pd.DataFrame
```

Produces dashboard dataset.

______________________________________________________________________

## create_charts()

```python
create_charts(
    df: pd.DataFrame
) -> None
```

Generates charts.

______________________________________________________________________

## summary_report()

```python
summary_report(
    df: pd.DataFrame
) -> dict
```

Returns summary statistics.

______________________________________________________________________

# 7. config Package

Provides centralized configuration.

Typical modules

```
constants.py

weights.py

portfolio.py

recommendations.py

logging.py
```

No public runtime API.

Import values directly.

Example

```python
from config.weights import EDGE_WEIGHT
```

______________________________________________________________________

# 8. utils Package

Reusable helper functions.

______________________________________________________________________

## get_logger()

```python
get_logger(
    name: str
) -> logging.Logger
```

Returns configured logger.

______________________________________________________________________

## safe_divide()

```python
safe_divide(
    numerator,
    denominator
)
```

Safely divides values while handling division by zero.

______________________________________________________________________

## validate_dataframe()

```python
validate_dataframe(
    df: pd.DataFrame,
    required_columns: list[str]
)
```

Raises an exception if required columns are missing.

______________________________________________________________________

## load_data()

```python
load_data(
    filename: str
) -> pd.DataFrame
```

Reads CSV or Excel files.

______________________________________________________________________

## save_data()

```python
save_data(
    df: pd.DataFrame,
    filename: str
)
```

Writes DataFrame to disk.

______________________________________________________________________

# 9. Main Application

______________________________________________________________________

## main()

Located in

```
strategy_comparison.py
```

Entry point.

Typical workflow

```
Load Data

↓

Calculate Metrics

↓

Compare Strategies

↓

Construct Portfolio

↓

Generate Reports
```

______________________________________________________________________

# 10. Exceptions

Typical exceptions

| Exception | Description |
|-----------|-------------|
| ValueError | Invalid values |
| KeyError | Missing columns |
| FileNotFoundError | Missing input file |
| RuntimeError | Processing failure |

Modules should raise informative exceptions.

______________________________________________________________________

# 11. Data Models

Primary object

```
pandas.DataFrame
```

Typical required columns

```
Stock

Expectancy%

Profit Factor

Reward Risk

Composite Score

Recommendation
```

All modules should preserve the DataFrame schema unless documented otherwise.

______________________________________________________________________

# 12. Return Types

| Function Category | Return Type |
|-------------------|------------|
| Metrics | DataFrame |
| Comparison | DataFrame |
| Portfolio | DataFrame |
| Statistics | dict |
| Correlation | DataFrame |
| Logger | Logger |
| Validation | None |
| Export | None |

______________________________________________________________________

# 13. Extension Guidelines

When adding new public APIs:

- Use descriptive names.
- Include type hints.
- Write Google- or NumPy-style docstrings.
- Validate all inputs.
- Raise meaningful exceptions.
- Add unit tests.
- Update this API reference.
- Maintain backward compatibility whenever possible.

______________________________________________________________________

# API Usage Example

```python
import pandas as pd

from derived_metrics import calculate_scores
from comparison import compare_strategies
from portfolio import allocate_portfolio
from reports import export_excel

# Load input data
df = pd.read_csv("strategy_results.csv")

# Calculate institutional scores
df = calculate_scores(df)

# Rank strategies
ranked = compare_strategies(df)

# Build portfolio
portfolio = allocate_portfolio(
    ranked,
    method="composite"
)

# Export results
export_excel(
    portfolio,
    "institutional_report.xlsx"
)
```

______________________________________________________________________

# API Design Principles

The public API is designed around the following principles:

- **Consistency:** Similar functions follow similar naming conventions and parameter patterns.
- **Composability:** Outputs from one module can be passed directly into the next without additional transformation.
- **Type Safety:** Public functions should use type hints and validate inputs.
- **Extensibility:** New metrics, allocation methods, and report types can be added without breaking existing APIs.
- **Backward Compatibility:** Public interfaces should remain stable across minor releases.

______________________________________________________________________

# Summary

The Institutional Strategy Comparison Platform exposes a clean, modular API for quantitative analysis, portfolio construction, and reporting. By maintaining clear interfaces, consistent data structures, and comprehensive documentation, the platform supports both standalone use and integration into larger analytical workflows.
