# Contributing Guide

First, thank you for your interest in contributing to the **Institutional Strategy Comparison Platform**.

We welcome bug reports, feature requests, documentation improvements, performance optimizations, and code contributions.

______________________________________________________________________

# Table of Contents

- Code of Conduct
- Development Environment
- Project Structure
- Coding Standards
- Branching Strategy
- Commit Message Convention
- Pull Requests
- Testing
- Documentation
- Reporting Issues

______________________________________________________________________

# Code of Conduct

Please be respectful and professional.

We expect contributors to:

- Be respectful to everyone.
- Provide constructive feedback.
- Write maintainable code.
- Follow the project standards.
- Keep discussions technical and professional.

______________________________________________________________________

# Development Environment

## Requirements

- Python 3.11+
- Git
- pip
- Virtual Environment

Clone the repository

```bash
git clone https://github.com/<username>/institutional-strategy-comparison-platform.git

cd institutional-strategy-comparison-platform
```

Create virtual environment

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

Install dependencies

```bash
pip install -e .[dev]
```

Install pre-commit

```bash
pre-commit install
```

______________________________________________________________________

# Project Structure

```text
comparison/
derived_metrics/
portfolio/
reports/
utils/
config/
tests/
docs/
examples/
```

Each module should have a single responsibility.

______________________________________________________________________

# Coding Standards

We follow:

- PEP 8
- Black
- Ruff
- MyPy

Formatting

```bash
black .
```

Linting

```bash
ruff check .
```

Type Checking

```bash
mypy .
```

______________________________________________________________________

# Code Style

Please:

- Use descriptive variable names.
- Add type hints to public functions.
- Write meaningful docstrings.
- Keep functions focused.
- Avoid duplicated code.
- Prefer reusable utility functions.

______________________________________________________________________

# Testing

Every new feature should include tests.

Run all tests

```bash
pytest
```

Coverage

```bash
pytest --cov
```

New modules should include:

- Unit tests
- Edge-case tests
- Error handling tests

______________________________________________________________________

# Branching Strategy

Use feature branches.

Examples

```text
feature/new-metric

feature/portfolio-optimizer

bugfix/export-error

docs/readme-update

refactor/math-utils
```

Avoid committing directly to the `main` branch.

______________________________________________________________________

# Commit Message Convention

Use concise, descriptive commit messages.

Examples

```text
feat: add Monte Carlo simulation

fix: correct portfolio allocation bug

docs: update README

refactor: simplify scoring engine

test: add robustness tests

ci: update GitHub Actions workflow
```

______________________________________________________________________

# Pull Requests

Before opening a Pull Request:

- Sync with the latest `main` branch.
- Ensure all tests pass.
- Run Black and Ruff.
- Update documentation if required.
- Include screenshots for UI changes (if applicable).

PR description should include:

- Summary of changes
- Motivation
- Testing performed
- Related issue(s)

______________________________________________________________________

# Documentation

If your contribution changes functionality, update:

- README.md
- CHANGELOG.md
- Docstrings
- Examples (if applicable)

______________________________________________________________________

# Reporting Issues

When reporting an issue, please include:

- Python version
- Operating System
- Error message
- Stack trace
- Steps to reproduce
- Expected behavior
- Actual behavior

______________________________________________________________________

# Feature Requests

Feature requests should explain:

- The problem
- Proposed solution
- Alternatives considered
- Expected benefits

______________________________________________________________________

# Development Workflow

1. Fork the repository.
1. Create a feature branch.
1. Make your changes.
1. Run formatting and tests.
1. Commit your work.
1. Push your branch.
1. Open a Pull Request.

______________________________________________________________________

# Thank You

Your contributions help improve the Institutional Strategy Comparison Platform and are greatly appreciated.
