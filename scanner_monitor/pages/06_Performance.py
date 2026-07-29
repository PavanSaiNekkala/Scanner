"""
06_Performance.py
=================

Institutional Performance Dashboard.

Provides comprehensive portfolio
performance analytics, benchmark
comparison, attribution analysis,
rolling metrics, and historical
performance reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.config import REPORTS_DIR
from core.helpers import first_existing
from core.helpers import numeric_series
from core.theme import apply_theme

from ui.cards import dashboard_header
from ui.cards import summary_row

from ui.sidebar import render_sidebar

from ui.tables import dataframe_info
from ui.tables import holdings_table

# ==========================================================
# Configuration
# ==========================================================


@dataclass(slots=True)
class PerformanceConfig:

    page_title: str = "Performance"

    page_icon: str = "📈"

    layout: str = "wide"

    portfolio_file: Path = (
        REPORTS_DIR
        / "latest"
        / "portfolio_summary.csv"
    )

    holdings_file: Path = (
        REPORTS_DIR
        / "latest"
        / "holdings.csv"
    )

    performance_file: Path = (
        REPORTS_DIR
        / "history"
        / "performance_history.csv"
    )


CONFIG = PerformanceConfig()

# ==========================================================
# Page
# ==========================================================

st.set_page_config(

    page_title=CONFIG.page_title,

    page_icon=CONFIG.page_icon,

    layout=CONFIG.layout,

)

apply_theme()

render_sidebar()

dashboard_header()

st.title("📈 Portfolio Performance Dashboard")

st.caption(
    "Institutional portfolio performance, "
    "benchmark analytics and attribution."
)

# ==========================================================
# Data Loading
# ==========================================================


@st.cache_data(show_spinner=False)
def load_csv(
    path: Path,
) -> pd.DataFrame:

    if path.exists():

        return pd.read_csv(path)

    return pd.DataFrame()


portfolio = load_csv(
    CONFIG.portfolio_file,
)

holdings = load_csv(
    CONFIG.holdings_file,
)

performance = load_csv(
    CONFIG.performance_file,
)
# ==========================================================
# Validation
# ==========================================================

if holdings.empty:

    st.warning(
        "No holdings available."
    )

    st.stop()

# ==========================================================
# Column Detection
# ==========================================================

symbol_col = first_existing(

    holdings,

    "Symbol",

    "Ticker",

    "Stock",

)

sector_col = first_existing(

    holdings,

    "Sector",

)

return_col = first_existing(

    holdings,

    "Return",

    "Return %",

    "P/L %",

)

weight_col = first_existing(

    holdings,

    "Weight",

    "Portfolio Weight",

)

market_value_col = first_existing(

    holdings,

    "Market Value",

    "Value",

)

date_col = first_existing(

    performance,

    "Date",

    "Timestamp",

)

# ==========================================================
# Numeric Series
# ==========================================================

returns = numeric_series(

    holdings,

    return_col,

)

weights = numeric_series(

    holdings,

    weight_col,

)

market_values = numeric_series(

    holdings,

    market_value_col,

)

# ==========================================================
# Executive KPIs
# ==========================================================

portfolio_value = market_values.sum()

average_return = (

    returns.mean()

    if len(returns)

    else 0

)

best_return = (

    returns.max()

    if len(returns)

    else 0

)

worst_return = (

    returns.min()

    if len(returns)

    else 0

)

winning_positions = int(

    (returns > 0).sum()

)

losing_positions = int(

    (returns < 0).sum()

)

summary_row(

    [

        (

            "Portfolio Value",

            f"{portfolio_value:,.0f}",

            None,

        ),

        (

            "Average Return",

            f"{average_return:.2f}%",

            None,

        ),

        (

            "Winning Positions",

            winning_positions,

            None,

        ),

        (

            "Losing Positions",

            losing_positions,

            None,

        ),

    ]

)

# ==========================================================
# Executive Performance Summary
# ==========================================================

st.divider()

st.header("Executive Performance Summary")

left_col, right_col = st.columns(
    [
        2,
        1,
    ]
)

performance_score = 50

if average_return > 0:

    performance_score += min(
        average_return,
        25,
    )

if winning_positions > losing_positions:

    performance_score += 15

if best_return > 15:

    performance_score += 10

performance_score = min(
    performance_score,
    100,
)

if performance_score >= 85:

    performance_rating = "EXCELLENT"

    rating_color = "#16A34A"

elif performance_score >= 70:

    performance_rating = "GOOD"

    rating_color = "#65A30D"

elif performance_score >= 55:

    performance_rating = "AVERAGE"

    rating_color = "#F59E0B"

else:

    performance_rating = "WEAK"

    rating_color = "#DC2626"

with left_col:

    summary_row(

        [

            (

                "Performance Score",

                f"{performance_score:.0f}",

                None,

            ),

            (

                "Best Position",

                f"{best_return:.2f}%",

                None,

            ),

            (

                "Worst Position",

                f"{worst_return:.2f}%",

                None,

            ),

            (

                "Average Return",

                f"{average_return:.2f}%",

                None,

            ),

        ]

    )

with right_col:

    st.markdown(

        f"""

<div
style="
background:{rating_color};
padding:24px;
border-radius:14px;
text-align:center;
color:white;
">

<h3>

Performance Rating

</h3>

<h1>

{performance_rating}

</h1>

<h2>

{performance_score:.0f}

</h2>

</div>

""",

        unsafe_allow_html=True,

    )

# ==========================================================
# Performance Gauge
# ==========================================================

st.divider()

st.header(
    "Performance Health",
)

gauge = go.Figure()

gauge.add_trace(

    go.Indicator(

        mode="gauge+number",

        value=performance_score,

        title={

            "text": "Performance Score",

        },

        gauge={

            "axis": {

                "range": [

                    0,

                    100,

                ],

            },

            "bar": {

                "color": rating_color,

            },

            "steps": [

                {

                    "range": [

                        0,

                        40,

                    ],

                    "color": "#FEE2E2",

                },

                {

                    "range": [

                        40,

                        60,

                    ],

                    "color": "#FEF3C7",

                },

                {

                    "range": [

                        60,

                        80,

                    ],

                    "color": "#DCFCE7",

                },

                {

                    "range": [

                        80,

                        100,

                    ],

                    "color": "#BBF7D0",

                },

            ],

        },

    )

)

gauge.update_layout(

    height=350,

    margin=dict(

        l=20,

        r=20,

        t=40,

        b=20,

    ),

)

st.plotly_chart(

    gauge,

    use_container_width=True,

)

# ==========================================================
# Equity Curve
# ==========================================================

st.divider()

st.header(
    "Equity Curve",
)

if (

    not performance.empty

    and date_col

):

    equity_col = first_existing(

        performance,

        "Portfolio Value",

        "Equity",

        "Portfolio",

        "NAV",

    )

    if equity_col:

        fig = px.line(

            performance,

            x=date_col,

            y=equity_col,

            markers=True,

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Portfolio Value",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    else:

        st.info(

            "Equity history unavailable."

        )

else:

    st.info(

        "Performance history unavailable."

    )

# ==========================================================
# Cumulative Returns
# ==========================================================

st.divider()

st.header(
    "Cumulative Returns",
)

if (

    not performance.empty

):

    history_return_col = first_existing(

        performance,

        "Daily Return",

        "Return",

        "Return %",

    )

    if history_return_col:

        cumulative = performance.copy()

        cumulative["Cumulative Return"] = (

            (

                1

                +

                cumulative[history_return_col]

                / 100

            )

            .cumprod()

            - 1

        ) * 100

        fig = px.area(

            cumulative,

            x=date_col,

            y="Cumulative Return",

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Return (%)",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Return Distribution
# ==========================================================

st.divider()

st.header(
    "Return Distribution",
)

left, right = st.columns(2)

with left:

    fig = px.histogram(

        returns,

        nbins=30,

    )

    fig.update_layout(

        height=400,

        xaxis_title="Return (%)",

        yaxis_title="Frequency",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

with right:

    fig = px.box(

        y=returns,

    )

    fig.update_layout(

        height=400,

        yaxis_title="Return (%)",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Return Statistics
# ==========================================================

st.divider()

st.header(
    "Performance Statistics",
)

volatility = (

    returns.std()

    if len(returns)

    else 0

)

median_return = (

    returns.median()

    if len(returns)

    else 0

)

positive_rate = (

    winning_positions

    /

    len(returns)

    * 100

    if len(returns)

    else 0

)

negative_rate = (

    losing_positions

    /

    len(returns)

    * 100

    if len(returns)

    else 0

)

summary_row(

    [

        (

            "Volatility",

            f"{volatility:.2f}%",

            None,

        ),

        (

            "Median Return",

            f"{median_return:.2f}%",

            None,

        ),

        (

            "Positive Rate",

            f"{positive_rate:.1f}%",

            None,

        ),

        (

            "Negative Rate",

            f"{negative_rate:.1f}%",

            None,

        ),

    ]

)

# ==========================================================
# Executive Commentary
# ==========================================================

st.subheader(
    "Performance Assessment",
)

if performance_rating == "EXCELLENT":

    st.success(

        "Portfolio performance is excellent with consistent positive returns and strong participation across holdings."

    )

elif performance_rating == "GOOD":

    st.success(

        "Portfolio performance remains healthy. Continue monitoring allocation and benchmark-relative returns."

    )

elif performance_rating == "AVERAGE":

    st.warning(

        "Performance is stable but there is room for improvement. Review lagging holdings and sector allocation."

    )

else:

    st.error(

        "Performance is below expectations. Consider portfolio rebalancing and reassessing underperforming positions."

    )

# ==========================================================
# Institutional Performance Metrics
# ==========================================================

st.divider()

st.header(
    "Institutional Performance Metrics",
)

risk_free_rate = 0.06

daily_rf = risk_free_rate / 252

daily_returns = returns / 100

if len(daily_returns):

    annual_return = (

        daily_returns.mean()

        * 252

    )

    annual_volatility = (

        daily_returns.std()

        * np.sqrt(252)

    )

else:

    annual_return = 0.0

    annual_volatility = 0.0

if annual_volatility > 0:

    sharpe_ratio = (

        annual_return

        - risk_free_rate

    ) / annual_volatility

else:

    sharpe_ratio = 0.0

downside_returns = daily_returns[
    daily_returns < 0
]

if len(downside_returns):

    downside_volatility = (

        downside_returns.std()

        * np.sqrt(252)

    )

else:

    downside_volatility = 0.0

if downside_volatility > 0:

    sortino_ratio = (

        annual_return

        - risk_free_rate

    ) / downside_volatility

else:

    sortino_ratio = 0.0


# ----------------------------------------------------------
# Maximum Drawdown
# ----------------------------------------------------------

if len(daily_returns):

    cumulative = (

        1

        + daily_returns

    ).cumprod()

    rolling_max = cumulative.cummax()

    drawdowns = (

        cumulative

        /

        rolling_max

        - 1

    )

    max_drawdown = abs(

        drawdowns.min()

    )

else:

    max_drawdown = 0.0

if max_drawdown > 0:

    calmar_ratio = (

        annual_return

        / max_drawdown

    )

else:

    calmar_ratio = 0.0

summary_row(

    [

        (

            "Sharpe",

            f"{sharpe_ratio:.2f}",

            None,

        ),

        (

            "Sortino",

            f"{sortino_ratio:.2f}",

            None,

        ),

        (

            "Calmar",

            f"{calmar_ratio:.2f}",

            None,

        ),

        (

            "Volatility",

            f"{annual_volatility*100:.2f}%",

            None,

        ),

    ]

)

# ==========================================================
# Alpha / Beta
# ==========================================================

st.divider()

st.header(
    "Benchmark Analytics",
)

benchmark_col = first_existing(

    performance,

    "Benchmark Return",

    "Index Return",

)

if (

    benchmark_col

    and

    len(performance)

):

    benchmark_returns = (

        pd.to_numeric(

            performance[benchmark_col],

            errors="coerce",

        )

        / 100

    )

    portfolio_returns = (

        pd.to_numeric(

            performance[history_return_col],

            errors="coerce",

        )

        / 100

    )

    aligned = pd.concat(

        [

            portfolio_returns,

            benchmark_returns,

        ],

        axis=1,

    ).dropna()

    if len(aligned) > 5:

        covariance = np.cov(

            aligned.iloc[:, 0],

            aligned.iloc[:, 1],

        )[0][1]

        variance = np.var(

            aligned.iloc[:, 1],

        )

        beta = (

            covariance

            / variance

            if variance

            else 0

        )

        alpha = (

            annual_return

            -

            (

                risk_free_rate

                +

                beta

                * (

                    benchmark_returns.mean()

                    * 252

                    -

                    risk_free_rate

                )

            )

        )

    else:

        alpha = 0

        beta = 0

else:

    alpha = 0

    beta = 0

summary_row(

    [

        (

            "Alpha",

            f"{alpha*100:.2f}%",

            None,

        ),

        (

            "Beta",

            f"{beta:.2f}",

            None,

        ),

        (

            "Annual Return",

            f"{annual_return*100:.2f}%",

            None,

        ),

        (

            "Risk-Free Rate",

            f"{risk_free_rate*100:.2f}%",

            None,

        ),

    ]

)

# ==========================================================
# Rolling Returns
# ==========================================================

st.divider()

st.header(
    "Rolling Performance",
)

if (

    history_return_col

    and

    len(performance) > 30

):

    rolling = performance.copy()

    rolling["Rolling Return"] = (

        (

            1

            +

            rolling[history_return_col]

            / 100

        )

        .rolling(20)

        .apply(

            np.prod,

            raw=True,

        )

        - 1

    ) * 100

    fig = px.line(

        rolling,

        x=date_col,

        y="Rolling Return",

    )

    fig.update_layout(

        height=420,

        xaxis_title="",

        yaxis_title="20-Day Rolling Return (%)",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Rolling Volatility
# ==========================================================

st.subheader(
    "Rolling Volatility",
)

if (

    history_return_col

    and

    len(performance) > 30

):

    rolling["Rolling Volatility"] = (

        rolling[history_return_col]

        .rolling(20)

        .std()

    )

    fig = px.line(

        rolling,

        x=date_col,

        y="Rolling Volatility",

    )

    fig.update_layout(

        height=420,

        xaxis_title="",

        yaxis_title="20-Day Volatility",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Rolling Drawdown
# ==========================================================

st.subheader(
    "Rolling Drawdown",
)

if (

    history_return_col

    and

    len(performance) > 30

):

    cumulative = (

        (

            1

            +

            rolling[history_return_col]

            / 100

        )

        .cumprod()

    )

    running_max = cumulative.cummax()

    rolling["Drawdown"] = (

        cumulative

        /

        running_max

        - 1

    ) * 100

    fig = px.area(

        rolling,

        x=date_col,

        y="Drawdown",

    )

    fig.update_layout(

        height=420,

        xaxis_title="",

        yaxis_title="Drawdown (%)",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Benchmark Comparison
# ==========================================================

st.divider()

st.header(
    "Portfolio vs Benchmark",
)

if (

    benchmark_col

    and

    history_return_col

    and

    len(performance)

):

    comparison = performance.copy()

    comparison["Portfolio"] = pd.to_numeric(

        comparison[history_return_col],

        errors="coerce",

    )

    comparison["Benchmark"] = pd.to_numeric(

        comparison[benchmark_col],

        errors="coerce",

    )

    comparison = comparison.dropna(

        subset=[

            "Portfolio",

            "Benchmark",

        ]

    )

    comparison["Portfolio Cumulative"] = (

        (

            1

            +

            comparison["Portfolio"]

            / 100

        )

        .cumprod()

        - 1

    ) * 100

    comparison["Benchmark Cumulative"] = (

        (

            1

            +

            comparison["Benchmark"]

            / 100

        )

        .cumprod()

        - 1

    ) * 100

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=comparison[date_col],

            y=comparison["Portfolio Cumulative"],

            mode="lines",

            name="Portfolio",

        )

    )

    fig.add_trace(

        go.Scatter(

            x=comparison[date_col],

            y=comparison["Benchmark Cumulative"],

            mode="lines",

            name="Benchmark",

        )

    )

    fig.update_layout(

        height=450,

        xaxis_title="",

        yaxis_title="Cumulative Return (%)",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Sector Performance Attribution
# ==========================================================

st.divider()

st.header(
    "Sector Attribution",
)

if (

    sector_col

    and

    return_col

    and

    weight_col

):

    sector_perf = (

        holdings

        .groupby(sector_col)

        .agg(

            Average_Return=(

                return_col,

                "mean",

            ),

            Portfolio_Weight=(

                weight_col,

                "sum",

            ),

            Holdings=(

                symbol_col,

                "count",

            ),

        )

        .reset_index()

    )

    sector_perf["Contribution"] = (

        sector_perf["Average_Return"]

        *

        sector_perf["Portfolio_Weight"]

        /

        100

    )

    fig = px.bar(

        sector_perf,

        x=sector_col,

        y="Contribution",

        color="Contribution",

        text="Contribution",

    )

    fig.update_layout(

        height=450,

        coloraxis_showscale=False,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

    holdings_table(

        sector_perf,
        key="sector_perf",

    )


# ==========================================================
# Winners vs Losers
# ==========================================================

st.divider()

st.header("Winners vs Losers")

top_winners = pd.DataFrame()
top_losers = pd.DataFrame()

# Determine return column if not already found
if (
    return_col is None
    or return_col not in holdings.columns
):

    for candidate in [
        "return",
        "returns",
        "Return",
        "Returns",
        "daily_return",
        "Daily Return",
        "pnl_pct",
        "PnL %",
        "gain_loss_pct",
        "Performance",
        "%",
    ]:

        if candidate in holdings.columns:
            return_col = candidate
            break

if (
    return_col is None
    or return_col not in holdings.columns
):

    st.info(
        "Return column not found. Unable to rank winners and losers."
    )

else:

    ranked = holdings.copy()

    ranked = ranked.sort_values(
        by=return_col,
        ascending=False,
    )

    top_winners = ranked.head(10)

    top_losers = ranked.tail(10)

    left, right = st.columns(2)

    with left:

        st.subheader("Top Winners")

        holdings_table(
            top_winners,
            key="top_winners",
        )

    with right:

        st.subheader("Top Losers")

        holdings_table(
            top_losers,
            key="top_losers",
        )
# ==========================================================
# Best / Worst Holdings
# ==========================================================

st.divider()

st.header("Performance Ranking")

left, right = st.columns(2)

with left:

    st.subheader("Top Winners")

    if (
        not top_winners.empty
        and symbol_col is not None
        and return_col is not None
        and symbol_col in top_winners.columns
        and return_col in top_winners.columns
    ):

        fig = px.bar(
            top_winners,
            x=return_col,
            y=symbol_col,
            orientation="h",
            color=return_col,
        )

        fig.update_layout(height=420)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("Winner data unavailable.")

with right:

    st.subheader("Top Losers")

    if (
        not top_losers.empty
        and symbol_col is not None
        and return_col is not None
        and symbol_col in top_losers.columns
        and return_col in top_losers.columns
    ):

        fig = px.bar(
            top_losers,
            x=return_col,
            y=symbol_col,
            orientation="h",
            color=return_col,
        )

        fig.update_layout(height=420)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("Loser data unavailable.")


# ==========================================================
# Performance Attribution Waterfall
# ==========================================================

st.divider()

st.header(
    "Performance Attribution",
)

if (

    sector_col

    and

    weight_col

    and

    return_col

):

    attribution = sector_perf.sort_values(

        "Contribution",

        ascending=False,

    )

    fig = go.Figure(

        go.Waterfall(

            x=attribution[sector_col],

            y=attribution["Contribution"],

            measure=[

                "relative"

            ]

            * len(attribution),

        )

    )

    fig.update_layout(

        height=450,

        showlegend=False,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Monthly Performance Heatmap
# ==========================================================

st.divider()

st.header(
    "Monthly Returns",
)

if (

    date_col

    and

    history_return_col

    and

    len(performance)

):

    monthly = performance.copy()

    monthly[date_col] = pd.to_datetime(

        monthly[date_col]

    )

    monthly["Year"] = monthly[date_col].dt.year

    monthly["Month"] = monthly[date_col].dt.strftime("%b")

    monthly = (

        monthly

        .groupby(

            [

                "Year",

                "Month",

            ]

        )[

            history_return_col

        ]

        .sum()

        .reset_index()

    )

    heatmap = monthly.pivot(

        index="Year",

        columns="Month",

        values=history_return_col,

    )

    fig = px.imshow(

        heatmap,

        text_auto=".1f",

        aspect="auto",

    )

    fig.update_layout(

        height=420,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Annual Performance
# ==========================================================

st.divider()

st.header(
    "Annual Performance",
)

if (

    date_col

    and

    history_return_col

    and

    len(performance)

):

    annual = performance.copy()

    annual[date_col] = pd.to_datetime(

        annual[date_col]

    )

    annual["Year"] = annual[date_col].dt.year

    annual = (

        annual

        .groupby("Year")[

            history_return_col

        ]

        .sum()

        .reset_index()

    )

    fig = px.bar(

        annual,

        x="Year",

        y=history_return_col,

        text=history_return_col,

        color=history_return_col,

    )

    fig.update_layout(

        height=420,

        coloraxis_showscale=False,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

# ==========================================================
# Historical Performance Dashboard
# ==========================================================

st.divider()

st.header("Historical Performance Dashboard")

required = {
    "Date": date_col,
    "Return": history_return_col,
}

missing = [
    name
    for name, col in required.items()
    if (
        col is None
        or col not in performance.columns
    )
]

if performance.empty:

    st.info("Historical performance data unavailable.")

elif missing:

    st.info(
        f"Historical dashboard unavailable. Missing column(s): {', '.join(missing)}"
    )

else:

    history = performance.copy()

    history[date_col] = pd.to_datetime(
        history[date_col],
        errors="coerce",
    )

    history = history.dropna(
        subset=[date_col]
    )

    metrics = pd.DataFrame(
        [
            ("Trading Days", len(history)),
            ("First Record", history[date_col].min()),
            ("Latest Record", history[date_col].max()),
            ("Best Daily Return", history[history_return_col].max()),
            ("Worst Daily Return", history[history_return_col].min()),
            ("Average Daily Return", history[history_return_col].mean()),
        ],
        columns=[
            "Metric",
            "Value",
        ],
    )

    left, right = st.columns([1, 2])

    with left:

        holdings_table(
            metrics,
            key="history_metrics",
        )

    with right:

        fig = px.line(
            history,
            x=date_col,
            y=history_return_col,
            markers=True,
        )

        fig.update_layout(
            height=430,
            xaxis_title="",
            yaxis_title="Daily Return (%)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

# ==========================================================
# Portfolio Diagnostics
# ==========================================================

st.divider()

st.header(
    "Performance Diagnostics",
)

diagnostics = pd.DataFrame(

    [

        (

            "Portfolio Positions",

            len(holdings),

        ),

        (

            "Winning Positions",

            winning_positions,

        ),

        (

            "Losing Positions",

            losing_positions,

        ),

        (

            "Average Return",

            average_return,

        ),

        (

            "Median Return",

            median_return,

        ),

        (

            "Best Return",

            best_return,

        ),

        (

            "Worst Return",

            worst_return,

        ),

        (

            "Annual Return",

            annual_return * 100,

        ),

        (

            "Annual Volatility",

            annual_volatility * 100,

        ),

        (

            "Sharpe Ratio",

            sharpe_ratio,

        ),

        (

            "Sortino Ratio",

            sortino_ratio,

        ),

        (

            "Calmar Ratio",

            calmar_ratio,

        ),

        (

            "Alpha",

            alpha,

        ),

        (

            "Beta",

            beta,

        ),

        (

            "Maximum Drawdown",

            max_drawdown * 100,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(

    diagnostics,
    key="diagnostics",

)

# ==========================================================
# Data Quality
# ==========================================================

st.divider()

st.header(
    "Data Quality",
)

quality = pd.DataFrame(

    [

        (

            "Portfolio Records",

            len(portfolio),

        ),

        (

            "Holdings Records",

            len(holdings),

        ),

        (

            "Performance Records",

            len(performance),

        ),

        (

            "Duplicate Holdings",

            holdings.duplicated().sum(),

        ),

        (

            "Missing Values",

            holdings.isna().sum().sum(),

        ),

        (

            "Missing Returns",

            returns.isna().sum(),

        ),

        (

            "Missing Weights",

            weights.isna().sum(),

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

left, right = st.columns(

    [

        2,

        1,

    ]

)

with left:

    holdings_table(

        quality,
        key="quality",

    )

with right:

    dataframe_info(

        holdings,

    )

# ==========================================================
# Download Center
# ==========================================================

st.divider()

st.header(
    "Download Center",
)

if CONFIG.performance_file.exists():

    with open(

        CONFIG.performance_file,

        "rb",

    ) as f:

        st.download_button(

            "Download Performance History",

            f,

            "performance_history.csv",

            "text/csv",

        )

if CONFIG.holdings_file.exists():

    with open(

        CONFIG.holdings_file,

        "rb",

    ) as f:

        st.download_button(

            "Download Holdings",

            f,

            "holdings.csv",

            "text/csv",

        )

if CONFIG.portfolio_file.exists():

    with open(

        CONFIG.portfolio_file,

        "rb",

    ) as f:

        st.download_button(

            "Download Portfolio Summary",

            f,

            "portfolio_summary.csv",

            "text/csv",

        )

# ==========================================================
# Institutional Insights
# ==========================================================

st.divider()

st.header(
    "Portfolio Insights",
)

insights = []

if sharpe_ratio >= 1.5:

    insights.append(

        "Excellent risk-adjusted performance."

    )

elif sharpe_ratio >= 1:

    insights.append(

        "Healthy risk-adjusted returns."

    )

else:

    insights.append(

        "Improve risk-adjusted returns."

    )

if winning_positions > losing_positions:

    insights.append(

        "Winning positions dominate the portfolio."

    )

else:

    insights.append(

        "Review underperforming holdings."

    )

if annual_return > 0.15:

    insights.append(

        "Annual return exceeds institutional target."

    )

elif annual_return > 0.08:

    insights.append(

        "Annual return is satisfactory."

    )

else:

    insights.append(

        "Portfolio growth is below target."

    )

if beta > 1.2:

    insights.append(

        "Portfolio is more volatile than benchmark."

    )

elif beta < 0.8:

    insights.append(

        "Portfolio is relatively defensive."

    )

if max_drawdown > 0.20:

    insights.append(

        "Large drawdown detected. Risk controls should be reviewed."

    )

for item in insights:

    st.info(item)

# ==========================================================
# Executive Summary
# ==========================================================

st.divider()

st.header(
    "Executive Summary",
)

summary = pd.DataFrame(

    [

        (

            "Performance Rating",

            performance_rating,

        ),

        (

            "Performance Score",

            performance_score,

        ),

        (

            "Annual Return",

            f"{annual_return*100:.2f}%",

        ),

        (

            "Sharpe Ratio",

            f"{sharpe_ratio:.2f}",

        ),

        (

            "Maximum Drawdown",

            f"{max_drawdown*100:.2f}%",

        ),

        (

            "Alpha",

            f"{alpha*100:.2f}%",

        ),

        (

            "Beta",

            f"{beta:.2f}",

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(

    summary,
    key="summary",

)

# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(

    "Institutional Scanner Monitor"

)

st.caption(

    "Performance Dashboard • Returns • Attribution • Benchmark Analysis • Risk-adjusted Performance"

)