# Frequently Asked Questions (FAQ)

## Institutional Strategy Comparison Platform V4

______________________________________________________________________

# Table of Contents

1. General Questions
1. Input Data
1. Metrics
1. Comparison Engine
1. Portfolio Engine
1. Reports
1. Performance
1. Troubleshooting
1. Best Practices
1. Future Plans

______________________________________________________________________

# 1. General Questions

## What is the Institutional Strategy Comparison Platform?

The Institutional Strategy Comparison Platform (ISCP) is a modular Python framework for evaluating, comparing, ranking, and reporting algorithmic trading strategies using institutional-grade quantitative metrics.

Unlike traditional backtest evaluators that rely on a few headline statistics, ISCP evaluates strategies across multiple dimensions, including profitability, reliability, efficiency, and overall quality.

______________________________________________________________________

## Who is this platform designed for?

The platform is suitable for:

- Quantitative analysts
- Algorithmic traders
- Portfolio managers
- Financial researchers
- Trading system developers
- Data scientists working with trading strategies

______________________________________________________________________

## What problems does ISCP solve?

The platform helps users:

- Compare multiple trading strategies objectively.
- Rank strategies using standardized metrics.
- Build rule-based portfolios.
- Generate professional reports.
- Reduce subjective decision-making.

______________________________________________________________________

# 2. Input Data

## What file formats are supported?

Supported formats:

- CSV (.csv)
- Excel (.xlsx)

Future versions may include:

- Parquet
- Feather
- SQL databases

______________________________________________________________________

## Which columns are required?

The exact schema depends on the workflow, but common required columns include:

- Stock
- Expectancy%
- Profit Factor
- Reward Risk
- Trades / Year
- Signal Quality
- Holding Efficiency

Additional columns may be required by specific modules.

______________________________________________________________________

## Can I use custom metrics?

Yes.

You can extend the `derived_metrics` package with your own metric calculations and incorporate them into the scoring pipeline.

______________________________________________________________________

# 3. Metrics

## Why isn't Win Rate enough?

A high Win Rate does not necessarily imply a profitable strategy.

Example:

- Strategy A wins 90% of trades but has large losses.
- Strategy B wins 55% of trades with significantly larger average wins.

Strategy B may have a higher Expectancy and be preferable.

ISCP evaluates multiple complementary metrics to avoid misleading conclusions.

______________________________________________________________________

## Why is Composite Score important?

Composite Score combines several normalized dimensions into a single ranking value.

It should be interpreted alongside:

- Edge Score
- Reliability Score
- Efficiency Score

rather than used in isolation.

______________________________________________________________________

## Can I change scoring weights?

Yes.

Scoring weights are defined in the `config` package and can be adjusted to suit different analytical preferences.

______________________________________________________________________

# 4. Comparison Engine

## How are strategies ranked?

Strategies are ranked primarily by Composite Score.

Secondary metrics such as Edge Score, Reliability Score, and Profit Factor may be used to break ties, depending on the configured ranking logic.

______________________________________________________________________

## What does "Strong Buy" mean?

"Strong Buy" indicates that a strategy meets the highest configured quality thresholds based on institutional scoring criteria.

Threshold values are configurable and should be calibrated using historical data.

______________________________________________________________________

## Can I compare multiple strategies for the same stock?

Yes.

The Comparison Engine supports evaluating multiple strategies applied to the same security and selecting the highest-ranked candidate according to the configured methodology.

______________________________________________________________________

# 5. Portfolio Engine

## How are portfolio weights calculated?

The platform supports several allocation methods, including:

- Equal Weight
- Composite Score Weight
- Edge Score Weight
- Reliability Weight
- Blended Weight

Each method is designed for different portfolio construction objectives.

______________________________________________________________________

## Do portfolio weights always sum to 100%?

Yes.

All allocation methods normalize weights so that the total allocation equals 100%.

______________________________________________________________________

## Can I limit the maximum position size?

Yes.

Portfolio constraints such as maximum and minimum position weights are configurable in the portfolio configuration.

______________________________________________________________________

# 6. Reports

## Which reports are generated?

Typical outputs include:

- Strategy rankings
- Portfolio allocations
- Summary statistics
- Excel workbooks
- Dashboard datasets
- Charts

______________________________________________________________________

## Can I customize reports?

Yes.

The Reporting Engine is modular and can be extended to include additional worksheets, visualizations, or export formats.

______________________________________________________________________

# 7. Performance

## How many strategies can the platform process?

The practical limit depends on available system resources, but the platform is designed to handle large datasets efficiently through vectorized pandas and NumPy operations.

______________________________________________________________________

## Why does processing become slower with larger datasets?

Performance may be affected by:

- Large Excel exports
- Complex chart generation
- Extensive correlation calculations
- Limited system memory

For large-scale analysis, consider exporting only the required reports or using more efficient storage formats.

______________________________________________________________________

# 8. Troubleshooting

## Missing required columns

**Error**

```text
KeyError: Required column not found
```

**Solution**

Verify that the input file contains all mandatory columns with the expected names and data types.

______________________________________________________________________

## Empty DataFrame

**Error**

```text
ValueError: Empty DataFrame
```

**Solution**

Ensure the input file contains data after any filtering or preprocessing steps.

______________________________________________________________________

## Invalid numeric values

**Error**

```text
ValueError: Cannot convert value to float
```

**Solution**

Check for missing values, text in numeric columns, or inconsistent formatting.

______________________________________________________________________

## Excel export fails

Possible causes:

- File is already open.
- Insufficient write permissions.
- Invalid output path.

Close the file if it is open and verify the destination directory.

______________________________________________________________________

## Portfolio weights do not total 100%

Ensure that:

- Weight normalization is applied.
- No invalid or negative weights are introduced.
- Allocation constraints are consistent.

______________________________________________________________________

# 9. Best Practices

- Validate input data before analysis.
- Keep configuration centralized.
- Use consistent column names.
- Review scoring thresholds periodically.
- Interpret Composite Score alongside component metrics.
- Maintain automated tests for custom extensions.
- Version-control configuration and documentation.

______________________________________________________________________

# 10. Future Plans

Planned enhancements include:

### Version 1.1

- Additional institutional metrics
- Improved report formatting
- Expanded chart library

### Version 2.0

- Walk-forward analysis
- Monte Carlo simulation
- Risk-parity allocation
- HTML and PDF reporting

### Version 3.0

- Machine learning ranking
- Real-time market data integration
- REST API
- Cloud deployment
- Interactive web dashboards

______________________________________________________________________

# Getting Help

Before reporting an issue:

1. Verify the input data format.
1. Review the configuration settings.
1. Run the automated test suite.
1. Check the generated log files.
1. Confirm that all project dependencies are installed.

If the issue persists, provide:

- Application version
- Operating system
- Python version
- Error message
- Sample input data (if appropriate)

This information helps reproduce and diagnose the problem more efficiently.

______________________________________________________________________

# Summary

This FAQ addresses the most common questions about the Institutional Strategy Comparison Platform. It covers data preparation, metrics, ranking, portfolio construction, reporting, troubleshooting, and recommended practices. As the platform evolves, this document should be updated to reflect new features, configuration options, and supported workflows.
