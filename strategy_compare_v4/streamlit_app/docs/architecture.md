# Architecture

## High-Level Architecture

```text
                CSV / Excel Reports
                        │
                        ▼
              ┌──────────────────┐
              │    Loader Service │
              └──────────────────┘
                        │
                        ▼
             ┌────────────────────┐
             │ Business Services  │
             │                    │
             │ Portfolio Service  │
             │ Report Service     │
             │ Cache Service      │
             └────────────────────┘
                        │
                        ▼
             ┌────────────────────┐
             │ Components         │
             │                    │
             │ Charts             │
             │ Cards              │
             │ Metrics            │
             │ Tables             │
             └────────────────────┘
                        │
                        ▼
              Streamlit Multi-Page UI
```

______________________________________________________________________

## Layers

### Presentation Layer

- Home
- Dashboard
- Strategy Pages
- Portfolio
- Reports

______________________________________________________________________

### Service Layer

Responsible for

- Loading reports
- Business logic
- Portfolio analytics
- Report management

______________________________________________________________________

### Utility Layer

Provides

- Formatting
- Validation
- Export
- Logging
- Calculations

______________________________________________________________________

### Data Layer

- CSV files
- Excel reports
- Session cache

______________________________________________________________________

## Design Principles

- Modular
- Reusable
- Testable
- Maintainable
- Enterprise-ready
