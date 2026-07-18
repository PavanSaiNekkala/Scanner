# Developer Guide

## Institutional Strategy Comparison Platform V4

---

# Table of Contents

1. Introduction
2. Development Environment
3. Project Structure
4. Architecture Overview
5. Coding Standards
6. Module Development
7. Adding a New Metric
8. Adding a New Comparison Engine
9. Adding a Portfolio Model
10. Adding a Report
11. Configuration Management
12. Logging
13. Testing
14. Documentation
15. Debugging
16. Performance Guidelines
17. Release Process

---

# 1. Introduction

This guide explains how to develop and extend the Institutional Strategy Comparison Platform.

The platform has been designed with modularity as the primary objective. Every feature should belong to exactly one module and have a single responsibility.

---

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

---

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

---

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

---

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

---

# 6. Module Development

Each module should:

- Have a single responsibility.
- Avoid circular imports.
- Import configuration from `config`.
- Reuse utilities from `utils`.
- Raise meaningful exceptions.
- Include unit tests.

---

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

---

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

---

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

---

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

---

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

---

# 12. Logging

Always use the centralized logger.

Example

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting comparison...")
```

Do not use `print()` for application logging.

---

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

---

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

---

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

---

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

---

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

---

# Best Practices

- Keep modules focused.
- Write reusable code.
- Prefer configuration over constants.
- Test all public functionality.
- Document every public function.
- Maintain backward compatibility where practical.

---

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

---

# Conclusion

The Institutional Strategy Comparison Platform is designed to be modular, extensible, and maintainable. By following the practices outlined in this guide, contributors can add new functionality while preserving consistency, code quality, and long-term maintainability.