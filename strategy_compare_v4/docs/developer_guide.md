# Developer Guide

## Institutional Strategy Comparison Platform V4

______________________________________________________________________

# Table of Contents

1. Introduction
1. Development Environment
1. Project Structure
1. Architecture Overview
1. Coding Standards
1. Module Development
1. Adding a New Metric
1. Adding a New Comparison Engine
1. Adding a Portfolio Model
1. Adding a Report
1. Configuration Management
1. Logging
1. Testing
1. Documentation
1. Debugging
1. Performance Guidelines
1. Release Process

______________________________________________________________________

# 1. Introduction

This guide explains how to develop and extend the Institutional Strategy Comparison Platform.

The platform has been designed with modularity as the primary objective. Every feature should belong to exactly one module and have a single responsibility.

______________________________________________________________________

# 2. Development Environment

## Requirements

- Python 3.11+
- Git
- Virtual Environment
- VS Code (Recommended)

Create environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install package

```bash
pip install -e .[dev]
```

Run tests

```bash
pytest
```

______________________________________________________________________

# 3. Project Structure

```
comparison/
config/
derived_metrics/
portfolio/
reports/
tests/
utils/
docs/
```

Each package has a clearly defined responsibility.

______________________________________________________________________

# 4. Architecture Overview

```
Input
   │
   ▼
Derived Metrics
   │
   ▼
Comparison
   │
   ▼
Portfolio
   │
   ▼
Reporting
```

Never bypass this processing flow.

______________________________________________________________________

# 5. Coding Standards

Follow:

- PEP 8
- Black formatting
- Ruff linting
- MyPy type checking

Rules

- Maximum line length: 88
- Use type hints
- Write docstrings
- Avoid duplicated code
- Keep functions small
- Prefer composition over inheritance

______________________________________________________________________

# 6. Module Development

Each module should:

- Have a single responsibility.
- Avoid circular imports.
- Import configuration from `config`.
- Reuse utilities from `utils`.
- Raise meaningful exceptions.
- Include unit tests.

______________________________________________________________________

# 7. Adding a New Metric

Place new metrics inside:

```
derived_metrics/
```

Example:

```python
def sharpe_ratio(df: pd.DataFrame) -> pd.Series:
    ...
```

Requirements

- Vectorized implementation
- Handle missing values
- Include documentation
- Add unit tests
- Update metric documentation

______________________________________________________________________

# 8. Adding a New Comparison Algorithm

Location

```
comparison/
```

Example

```
comparison/
    ranking_v2.py
```

Responsibilities

- Rank strategies
- Return DataFrame
- Preserve schema
- Avoid modifying inputs

______________________________________________________________________

# 9. Adding a Portfolio Model

Location

```
portfolio/
```

Example

```
risk_parity.py
```

Guidelines

- Normalize weights
- Validate inputs
- Return percentage weights
- Sum should equal 100%

______________________________________________________________________

# 10. Adding Reports

Location

```
reports/
```

Reports may include

- Excel
- PDF (future)
- Dashboard
- Charts

Every report should

- Accept DataFrame input
- Validate columns
- Handle empty datasets
- Raise clear exceptions

______________________________________________________________________

# 11. Configuration

Do not hard-code values.

Use

```
config/
```

Examples

- Thresholds
- Weights
- Recommendation limits
- Constants

______________________________________________________________________

# 12. Logging

Always use the centralized logger.

Example

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting comparison...")
```

Do not use `print()` for application logging.

______________________________________________________________________

# 13. Testing

Every feature must include tests.

Run

```bash
pytest
```

Coverage

```bash
pytest --cov
```

Test types

- Unit
- Edge Cases
- Regression
- Error Handling

______________________________________________________________________

# 14. Documentation

Update documentation when

- Adding modules
- Adding metrics
- Changing formulas
- Modifying configuration

Keep

- README
- API Reference
- Metric Guide

synchronized with the code.

______________________________________________________________________

# 15. Debugging

Useful commands

Run formatter

```bash
black .
```

Run Ruff

```bash
ruff check .
```

Run MyPy

```bash
mypy .
```

Run tests

```bash
pytest
```

______________________________________________________________________

# 16. Performance Guidelines

Prefer

- Vectorized pandas operations
- NumPy operations
- Batch processing

Avoid

- Nested loops over DataFrames
- Repeated DataFrame copies
- Hard-coded values
- Global mutable state

______________________________________________________________________

# 17. Release Process

Before releasing:

- All tests pass
- Documentation updated
- CHANGELOG updated
- Version incremented
- CI pipeline passes
- Git tag created

Example

```bash
git tag v1.0.0

git push origin v1.0.0
```

______________________________________________________________________

# Best Practices

- Keep modules focused.
- Write reusable code.
- Prefer configuration over constants.
- Test all public functionality.
- Document every public function.
- Maintain backward compatibility where practical.

______________________________________________________________________

# Directory Ownership

| Directory | Responsibility |
|-----------|----------------|
| comparison | Ranking and analysis |
| derived_metrics | Metric calculations |
| portfolio | Portfolio construction |
| reports | Outputs and visualization |
| config | Constants and thresholds |
| utils | Shared helper functions |
| tests | Automated testing |
| docs | Project documentation |

______________________________________________________________________

# Conclusion

The Institutional Strategy Comparison Platform is designed to be modular, extensible, and maintainable. By following the practices outlined in this guide, contributors can add new functionality while preserving consistency, code quality, and long-term maintainability.
