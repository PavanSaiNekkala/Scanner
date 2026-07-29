"""
Application constants.
"""

# ==========================================================
# Recommendation Signals
# ==========================================================

SIGNALS = [

    "STRONG BUY",

    "BUY",

    "WATCH",

    "AVOID",

    "SELL",

]

# ==========================================================
# Themes
# ==========================================================

DEFAULT_THEME = "light"

# ==========================================================
# Date Formats
# ==========================================================

DATE_FORMAT = "%d %b %Y"

DATETIME_FORMAT = "%d %b %Y %H:%M:%S"

# ==========================================================
# Number Formatting
# ==========================================================

PERCENT_COLUMNS = [

    "Return",

    "Daily Return",

    "Monthly Return",

    "Annual Return",

    "Weight",

    "Portfolio Weight",

    "Target",

    "Exposure",

    "Drawdown",

    "Risk",

    "Volatility",

]

CURRENCY_COLUMNS = [

    "Market Value",

    "Investment",

    "Portfolio Value",

    "Cash",

    "PnL",

    "Profit",

    "Loss",

]

INTEGER_COLUMNS = [

    "Quantity",

    "Shares",

    "Trades",

    "Orders",

]

# ==========================================================
# Dashboard Colours
# ==========================================================

BUY_COLOR = "#16A34A"

WATCH_COLOR = "#F59E0B"

SELL_COLOR = "#DC2626"

PRIMARY_COLOR = "#2563EB"

SECONDARY_COLOR = "#6366F1"

SUCCESS_COLOR = "#16A34A"

WARNING_COLOR = "#F59E0B"

ERROR_COLOR = "#DC2626"

INFO_COLOR = "#0284C7"

# ==========================================================
# Risk Thresholds
# ==========================================================

LOW_RISK = 30

MEDIUM_RISK = 60

HIGH_RISK = 80

# ==========================================================
# Dashboard Ratings
# ==========================================================

EXCELLENT = 90

GOOD = 75

AVERAGE = 60

POOR = 40

# ==========================================================
# Default Tables
# ==========================================================

DEFAULT_PAGE_SIZE = 20

MAX_PREVIEW_ROWS = 20

# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_DOWNLOADS = [

    ".csv",

    ".xlsx",

    ".xls",

    ".parquet",

    ".json",

    ".txt",

    ".pdf",

]

# ==========================================================
# Portfolio Defaults
# ==========================================================

DEFAULT_CASH = 100000

DEFAULT_BENCHMARK = "NIFTY 50"

DEFAULT_CURRENCY = "INR"

# ==========================================================
# Application Information
# ==========================================================

APP_NAME = "Institutional Scanner Monitor"

APP_VERSION = "1.0.0"