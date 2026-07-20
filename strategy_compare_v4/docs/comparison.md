# Comparison Engine

## Institutional Strategy Comparison Platform V4

______________________________________________________________________

# Table of Contents

1. Overview
1. Objectives
1. Comparison Workflow
1. Comparison Modules
1. Ranking Methodology
1. Composite Score
1. Leaderboards
1. Correlation Analysis
1. Robustness Analysis
1. Recommendation Engine
1. Output Schema
1. Performance Considerations
1. Best Practices

______________________________________________________________________

# 1. Overview

The Comparison Engine is responsible for transforming calculated strategy metrics into actionable rankings and recommendations.

Instead of evaluating strategies using a single statistic such as Win Rate or CAGR, the engine considers multiple institutional-quality dimensions to provide a balanced assessment.

The engine integrates outputs from the Derived Metrics module and produces ranked datasets for portfolio construction and reporting.

______________________________________________________________________

# 2. Objectives

The Comparison Engine is designed to:

- Rank trading strategies consistently.
- Compare strategies across multiple metrics.
- Evaluate overall quality using composite scoring.
- Identify robust and repeatable strategies.
- Generate institutional recommendations.
- Provide inputs for portfolio allocation.

______________________________________________________________________

# 3. Comparison Workflow

```
Derived Metrics
       │
       ▼
Validation
       │
       ▼
Score Normalization
       │
       ▼
Composite Score Calculation
       │
       ▼
Ranking
       │
       ▼
Recommendation Assignment
       │
       ▼
Portfolio Engine
```

______________________________________________________________________

# 4. Comparison Modules

## strategy_compare.py

Responsibilities

- Compare all strategies.
- Calculate institutional ranking.
- Generate recommendation.

Input

- Strategy metrics DataFrame.

Output

- Ranked strategy DataFrame.

______________________________________________________________________

## stock_compare.py

Responsibilities

- Compare stocks across strategies.
- Identify strongest candidates.
- Aggregate multiple strategies.

______________________________________________________________________

## leaderboard.py

Generates leaderboards.

Examples

- Top 10 Strategies
- Top 20 Stocks
- Highest Composite Score
- Highest Expectancy
- Highest Profit Factor

______________________________________________________________________

## robustness.py

Evaluates consistency.

Typical considerations

- Trade frequency
- Stability
- Reliability
- Metric consistency

______________________________________________________________________

## correlation.py

Measures similarity between strategies.

Used for

- Diversification
- Portfolio optimization
- Reducing overlap

______________________________________________________________________

# 5. Ranking Methodology

The platform ranks strategies using multiple institutional metrics.

Primary Metrics

- Composite Score
- Edge Score
- Reliability Score
- Efficiency Score

Secondary Metrics

- Expectancy
- Profit Factor
- Reward Risk
- Profit Velocity
- Trades per Year

Tie Breakers

1. Higher Composite Score
1. Higher Edge Score
1. Higher Reliability Score
1. Higher Profit Factor
1. Higher Expectancy

______________________________________________________________________

# 6. Composite Score

The Composite Score combines multiple dimensions of strategy quality into a single ranking metric.

Inputs include:

- Edge Score
- Reliability Score
- Efficiency Score

Additional weighting may include:

- Expectancy
- Profit Factor
- Reward Risk
- Profit Velocity

The weighting scheme is configurable in:

```
config/weights.py
```

Composite Score should always be interpreted alongside the underlying component scores rather than in isolation.

______________________________________________________________________

# 7. Leaderboards

The engine generates several leaderboards.

Examples

### Overall Ranking

Ranks strategies by Composite Score.

### Edge Leaderboard

Ranks strategies by Edge Score.

### Reliability Leaderboard

Ranks strategies by Reliability Score.

### Efficiency Leaderboard

Ranks strategies by Efficiency Score.

### Profitability Leaderboard

Ranks by:

- Expectancy
- Profit Factor
- Reward Risk

______________________________________________________________________

# 8. Correlation Analysis

Purpose

Correlation analysis identifies similarity between strategies.

Applications

- Diversification
- Portfolio construction
- Strategy clustering
- Redundancy detection

Interpretation

| Correlation | Meaning |
|-------------|---------|
| 1.00 | Identical behaviour |
| 0.70–0.99 | Highly correlated |
| 0.30–0.69 | Moderately correlated |
| 0.00–0.29 | Weakly correlated |
| Negative | Opposing behaviour |

Lower correlation generally improves portfolio diversification.

______________________________________________________________________

# 9. Robustness Analysis

Robustness measures whether strategy performance is likely to remain stable under different market conditions.

Factors considered include:

- Number of trades
- Consistency
- Stability
- Reliability
- Holding efficiency
- Exit behaviour

Strategies with higher robustness are generally preferred over strategies with highly volatile performance.

______________________________________________________________________

# 10. Recommendation Engine

Recommendations translate quantitative scores into actionable categories.

Typical recommendation levels

| Recommendation | Meaning |
|---------------|---------|
| Strong Buy | Exceptional strategy with high institutional quality |
| Buy | Strong candidate for deployment |
| Watch | Monitor for further confirmation |
| Improve | Requires optimization before use |
| Avoid | Does not meet institutional standards |

Threshold values are defined in:

```
config/recommendations.py
```

______________________________________________________________________

# 11. Output Schema

Typical output columns

| Column | Description |
|---------|-------------|
| Institution Rank | Final ranking |
| Strategy | Strategy name |
| Stock | Stock symbol |
| Composite Score | Overall quality score |
| Edge Score | Edge evaluation |
| Reliability Score | Stability assessment |
| Efficiency Score | Capital efficiency |
| Expectancy | Expected profit per trade |
| Profit Factor | Gross profit / gross loss |
| Reward Risk | Average reward-to-risk ratio |
| Recommendation | Institutional recommendation |

The output DataFrame serves as the primary input for the Portfolio Engine and Reporting Engine.

______________________________________________________________________

# 12. Performance Considerations

The Comparison Engine is optimized using:

- Vectorized pandas operations
- NumPy computations
- Minimal DataFrame copying
- Modular processing pipeline

Avoid:

- Row-wise loops
- Repeated sorting
- Hard-coded thresholds

______________________________________________________________________

# 13. Best Practices

- Always validate input data before comparison.
- Keep scoring weights configurable.
- Interpret Composite Score together with component metrics.
- Use correlation analysis when constructing diversified portfolios.
- Document any changes to ranking methodology.
- Maintain backward compatibility where practical.

______________________________________________________________________

# Summary

The Comparison Engine is the analytical core of the Institutional Strategy Comparison Platform. By combining multiple quantitative dimensions into standardized rankings and recommendations, it enables objective strategy evaluation, robust portfolio construction, and consistent reporting across a wide range of trading systems.
