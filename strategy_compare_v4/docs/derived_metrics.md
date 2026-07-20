# Derived Metrics

## Institutional Strategy Comparison Platform V4

______________________________________________________________________

# Table of Contents

1. Introduction
1. Metric Categories
1. Performance Metrics
1. Risk Metrics
1. Exit Metrics
1. Opportunity Metrics
1. Validation Metrics
1. Scoring Metrics
1. Composite Scoring
1. Metric Interpretation
1. Best Practices
1. References

______________________________________________________________________

# 1. Introduction

The Derived Metrics Engine transforms raw backtest statistics into standardized institutional-quality performance indicators.

These metrics provide a multidimensional assessment of trading strategies, allowing comparison beyond simple profitability measures.

Unlike traditional evaluations based solely on Win Rate or CAGR, the platform measures:

- Profitability
- Risk
- Consistency
- Reliability
- Efficiency
- Opportunity
- Overall Quality

These derived metrics form the foundation of the Comparison Engine, Portfolio Engine, and Reporting modules.

______________________________________________________________________

# 2. Metric Categories

The metrics are grouped into six categories.

| Category | Purpose |
|----------|----------|
| Performance | Profitability and returns |
| Risk | Downside and consistency |
| Exit | Trade exit behaviour |
| Opportunity | Trading frequency and efficiency |
| Validation | Data quality and statistical confidence |
| Scoring | Institutional rankings |

______________________________________________________________________

# 3. Performance Metrics

Performance metrics evaluate how effectively a strategy generates returns.

______________________________________________________________________

## Expectancy

### Purpose

Measures the average expected profit or loss per trade.

### Formula

```
Expectancy =

(Win Rate × Average Win)

−

(Loss Rate × Average Loss)
```

### Interpretation

Higher values indicate better expected profitability.

### Good Values

| Expectancy | Interpretation |
|------------|---------------|
| > 3 | Excellent |
| 2–3 | Very Good |
| 1–2 | Good |
| 0–1 | Weak |
| < 0 | Losing Strategy |

______________________________________________________________________

## Profit Factor

### Purpose

Measures gross profits relative to gross losses.

### Formula

```
Profit Factor

=

Gross Profit

/

Gross Loss
```

### Interpretation

| PF | Quality |
|----|---------|
| >3 | Exceptional |
| 2–3 | Strong |
| 1.5–2 | Good |
| 1–1.5 | Acceptable |
| \<1 | Losing |

______________________________________________________________________

## Reward Risk

### Purpose

Measures average reward relative to average loss.

### Formula

```
Average Win

/

Average Loss
```

### Interpretation

Higher values indicate better trade quality.

______________________________________________________________________

## Profit Velocity

### Purpose

Measures profitability generated per unit time.

### Typical Formula

```
Net Profit

/

Trading Period
```

Higher values indicate faster capital growth.

______________________________________________________________________

# 4. Risk Metrics

Risk metrics evaluate downside exposure and consistency.

______________________________________________________________________

## Drawdown

Maximum decline from an equity peak.

Lower values are preferable.

______________________________________________________________________

## Drawdown Recovery

Measures how quickly losses are recovered.

Higher values indicate resilient strategies.

______________________________________________________________________

## Stability Score

Measures consistency of returns.

High Stability Score implies repeatable performance.

______________________________________________________________________

## Risk Score

Institutional measure combining multiple downside indicators.

Lower downside risk produces higher Risk Score.

______________________________________________________________________

# 5. Exit Metrics

Exit behaviour provides insight into strategy execution quality.

______________________________________________________________________

## Winning Exit %

Percentage of trades exiting through profit targets.

Higher values indicate disciplined profit-taking.

______________________________________________________________________

## Losing Exit %

Percentage of trades closed by stop loss.

Lower values are generally preferred.

______________________________________________________________________

## Time Exit %

Percentage of trades closed due to time-based exits.

Useful for analysing holding behaviour.

______________________________________________________________________

## Trailing Exit %

Percentage of trades exited via trailing stop.

Higher values often indicate trend-following characteristics.

______________________________________________________________________

## Target Exit %

Measures proportion of trades achieving predefined targets.

______________________________________________________________________

## Stop Exit %

Measures stop-loss frequency.

Useful for evaluating risk management.

______________________________________________________________________

# 6. Opportunity Metrics

These metrics measure trading opportunities and capital utilisation.

______________________________________________________________________

## Trades Per Year

Average annual trading frequency.

Interpretation

| Trades | Meaning |
|---------|---------|
| >200 | Very Active |
| 100–200 | Active |
| 50–100 | Moderate |
| \<50 | Low Frequency |

______________________________________________________________________

## Signal Quality

Measures effectiveness of generated trade signals.

High Signal Quality indicates fewer false signals.

______________________________________________________________________

## Holding Efficiency

Evaluates profitability relative to average holding period.

Higher values imply efficient capital usage.

______________________________________________________________________

## Opportunity Score

Institutional measure of opportunity generation.

Combines

- Frequency
- Efficiency
- Signal Quality

______________________________________________________________________

# 7. Validation Metrics

Validation metrics ensure statistical confidence.

Examples include

- Minimum Trade Count
- Data Completeness
- Missing Values
- Outlier Detection
- Consistency Checks

Strategies failing validation should not be ranked.

______________________________________________________________________

# 8. Scoring Metrics

Institutional scores are normalized metrics.

______________________________________________________________________

## Edge Score

Measures sustainable trading edge.

Inputs may include

- Expectancy
- Profit Factor
- Reward Risk

Higher values indicate stronger competitive advantage.

______________________________________________________________________

## Reliability Score

Measures repeatability.

Factors include

- Stability
- Drawdown
- Trade Count
- Validation

______________________________________________________________________

## Efficiency Score

Measures capital efficiency.

Inputs include

- Holding Efficiency
- Signal Quality
- Opportunity Score

______________________________________________________________________

## Composite Score

Overall institutional ranking.

Combines

- Edge Score
- Reliability Score
- Efficiency Score

Weights are configurable in:

```
config/weights.py
```

______________________________________________________________________

# 9. Composite Scoring

Composite Score provides a single ranking metric while preserving multidimensional analysis.

Typical workflow

```
Normalize Metrics

↓

Apply Weights

↓

Calculate Category Scores

↓

Aggregate Scores

↓

Composite Score
```

Composite Score should always be interpreted alongside component scores.

______________________________________________________________________

# 10. Metric Interpretation

Institutional evaluation considers all metrics collectively.

Example

```
High Expectancy

+

Low Reliability

=

Needs Further Validation
```

```
Moderate Expectancy

+

Excellent Reliability

=

Institutional Candidate
```

Balanced strategies are generally preferred over highly optimized but unstable strategies.

______________________________________________________________________

# 11. Best Practices

- Never evaluate using a single metric.
- Validate data before scoring.
- Normalize metrics before comparison.
- Review component scores alongside Composite Score.
- Periodically recalibrate thresholds.
- Document any formula changes.

______________________________________________________________________

# 12. References

Recommended reading

- Ralph Vince – Portfolio Management Formulas
- Van Tharp – Trade Your Way to Financial Freedom
- Ernest Chan – Quantitative Trading
- Marcos López de Prado – Advances in Financial Machine Learning
- CFA Institute – Portfolio Management Standards

______________________________________________________________________

# Summary

The Derived Metrics Engine provides the quantitative foundation of the Institutional Strategy Comparison Platform. By converting raw backtest statistics into standardized institutional metrics, it enables objective strategy evaluation, consistent ranking, robust portfolio construction, and professional reporting.
