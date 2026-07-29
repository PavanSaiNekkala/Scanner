"""
05_Risk.py
==========

Institutional Risk Dashboard.

Provides portfolio risk monitoring,
drawdown analysis,
exposure monitoring,
stress testing,
and institutional risk reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

from core.config import REPORTS_DIR
from core.helpers import first_existing
from core.helpers import numeric_series
from core.theme import apply_theme

from ui.cards import dashboard_header
from ui.cards import summary_row

from ui.sidebar import render_sidebar

from ui.tables import dataframe_info
from ui.tables import holdings_table

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------


@dataclass(slots=True)
class RiskConfig:

    page_title: str = "Risk"

    page_icon: str = "⚠️"

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

    risk_file: Path = (
        REPORTS_DIR
        / "latest"
        / "risk_summary.csv"
    )


CONFIG = RiskConfig()

# -------------------------------------------------------
# Page
# -------------------------------------------------------

st.set_page_config(

    page_title=CONFIG.page_title,

    page_icon=CONFIG.page_icon,

    layout=CONFIG.layout,

)

apply_theme()

render_sidebar()

dashboard_header()

st.title("⚠️ Portfolio Risk Dashboard")

st.caption(
    "Institutional risk analytics, exposure monitoring, "
    "portfolio diagnostics and stress testing."
)

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:

    if path.exists():

        return pd.read_csv(path)

    return pd.DataFrame()


portfolio = load_csv(CONFIG.portfolio_file)

holdings = load_csv(CONFIG.holdings_file)

risk = load_csv(CONFIG.risk_file)

if holdings.empty:

    st.warning(
        "No holdings available."
    )

    st.stop()

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

weight_col = first_existing(

    holdings,

    "Weight",

    "Portfolio Weight",

)

return_col = first_existing(

    holdings,

    "Return",

    "P/L %",

)

market_value_col = first_existing(

    holdings,

    "Market Value",

    "Value",

)

weights = numeric_series(

    holdings,

    weight_col,

)

returns = numeric_series(

    holdings,

    return_col,

)

market_values = numeric_series(

    holdings,

    market_value_col,

)

portfolio_value = market_values.sum()

largest_position = weights.max()

average_weight = weights.mean()

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

            "Largest Position",

            f"{largest_position:.2f}%",

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
# Executive Risk Summary
# ==========================================================

st.divider()

st.header("Executive Risk Summary")

col1, col2 = st.columns(
    [
        2,
        1,
    ]
)

position_count = len(holdings)

sector_count = (
    holdings[sector_col].nunique()
    if sector_col
    else 0
)

largest_weight = (
    weights.max()
    if not weights.empty
    else 0
)

top5_weight = (
    weights.nlargest(5).sum()
    if len(weights)
    else 0
)

avg_weight = (
    weights.mean()
    if len(weights)
    else 0
)

# ----------------------------------------------------------
# Diversification Score
# ----------------------------------------------------------

if position_count >= 40:

    diversification_score = 100

elif position_count >= 30:

    diversification_score = 90

elif position_count >= 20:

    diversification_score = 75

elif position_count >= 10:

    diversification_score = 60

else:

    diversification_score = 40

if largest_weight > 12:

    diversification_score -= 15

elif largest_weight > 8:

    diversification_score -= 8

if top5_weight > 50:

    diversification_score -= 10

diversification_score = max(
    diversification_score,
    0,
)

# ----------------------------------------------------------
# Concentration Score
# ----------------------------------------------------------

concentration_score = max(
    0,
    100 - top5_weight,
)

# ----------------------------------------------------------
# Portfolio Health
# ----------------------------------------------------------

portfolio_health = (

    diversification_score * 0.45

    + concentration_score * 0.30

    + min(
        sector_count * 5,
        25,
    )

)

portfolio_health = round(
    portfolio_health,
    1,
)

# ----------------------------------------------------------
# Risk Level
# ----------------------------------------------------------

if portfolio_health >= 85:

    risk_level = "LOW"

    risk_color = "#16A34A"

elif portfolio_health >= 70:

    risk_level = "MODERATE"

    risk_color = "#F59E0B"

elif portfolio_health >= 55:

    risk_level = "HIGH"

    risk_color = "#EF4444"

else:

    risk_level = "CRITICAL"

    risk_color = "#991B1B"

# ==========================================================
# Portfolio Health Gauge
# ==========================================================

gauge = go.Figure()

gauge.add_trace(

    go.Indicator(

        mode="gauge+number",

        value=portfolio_health,

        title={

            "text": "Portfolio Health Score",

        },

        gauge={

            "axis": {

                "range": [

                    0,

                    100,

                ],

            },

            "bar": {

                "color": risk_color,

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

                    "color": "#FDE68A",

                },

                {

                    "range": [

                        60,

                        80,

                    ],

                    "color": "#D9F99D",

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

        t=50,

        b=20,

    ),

)

st.plotly_chart(

    gauge,

    use_container_width=True,

)

# ==========================================================
# Executive Commentary
# ==========================================================

st.subheader("Risk Assessment")

if risk_level == "LOW":

    st.success(

        "Portfolio is well diversified with acceptable "
        "concentration risk and healthy sector allocation."

    )

elif risk_level == "MODERATE":

    st.warning(

        "Portfolio concentration is beginning to increase. "
        "Monitor position sizing and sector exposure."

    )

elif risk_level == "HIGH":

    st.error(

        "Risk concentration is elevated. Consider reducing "
        "large positions and improving diversification."

    )

else:

    st.error(

        "Portfolio risk is critically high. Immediate "
        "portfolio rebalancing is recommended."

    )

# ==========================================================
# Portfolio Exposure Analytics
# ==========================================================

st.divider()

st.header("Portfolio Exposure Analytics")

left_col, right_col = st.columns(
    [
        1,
        1,
    ]
)

# ----------------------------------------------------------
# Sector Exposure
# ----------------------------------------------------------

if sector_col:

    sector_exposure = (

        holdings.groupby(
            sector_col,
            dropna=False,
        )[weight_col]
        .sum()
        .sort_values(
            ascending=False,
        )
        .reset_index()
    )

else:

    sector_exposure = pd.DataFrame()

# ----------------------------------------------------------
# Position Exposure
# ----------------------------------------------------------

position_exposure = holdings.copy()

if weight_col:

    position_exposure = (

        position_exposure.sort_values(

            weight_col,

            ascending=False,

        )

    )

top_positions = position_exposure.head(
    15,
)

top_positions = top_positions.copy()

top_positions[weight_col] = (
    top_positions[weight_col]
    .astype(str)
    .str.replace("%", "", regex=False)
    .str.replace(",", "", regex=False)
)

top_positions[weight_col] = pd.to_numeric(
    top_positions[weight_col],
    errors="coerce",
)

top_positions = top_positions.dropna(
    subset=[symbol_col, weight_col]
)

with left_col:

    st.subheader("Sector Allocation")

    if not sector_exposure.empty:

        fig = px.bar(

            sector_exposure,

            x=sector_col,

            y=weight_col,

            color=weight_col,

            text=weight_col,

        )

        fig.update_layout(

            height=420,

            xaxis_title="",

            yaxis_title="Portfolio Weight (%)",

            coloraxis_showscale=False,

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

            textposition="outside",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    else:

        st.info(

            "Sector information unavailable."

        )

with right_col:

    st.subheader("Top Position Exposure")

    if not top_positions.empty:

        fig = px.bar(

            top_positions,

            x=weight_col,

            y=symbol_col,

            orientation="h",

            color=weight_col,

            text=weight_col,

        )

        fig.update_layout(

            height=420,

            yaxis=dict(

                autorange="reversed",

            ),

            xaxis_title="Portfolio Weight (%)",

            yaxis_title="",

            coloraxis_showscale=False,

        )

        fig.update_traces(

            texttemplate="%{text:.2f}",

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

    else:

        st.info(

            "No position data available."

        )

# ==========================================================
# Concentration Analysis
# ==========================================================

st.subheader("Position Concentration")

c1, c2, c3, c4 = st.columns(4)

top1 = weights.nlargest(1).sum()

top3 = weights.nlargest(3).sum()

top5 = weights.nlargest(5).sum()

top10 = weights.nlargest(10).sum()

c1.metric(

    "Top 1",

    f"{top1:.2f}%",

)

c2.metric(

    "Top 3",

    f"{top3:.2f}%",

)

c3.metric(

    "Top 5",

    f"{top5:.2f}%",

)

c4.metric(

    "Top 10",

    f"{top10:.2f}%",

)

# ==========================================================
# Diversification Statistics
# ==========================================================

weights_decimal = (

    weights / 100

    if len(weights)

    else pd.Series(dtype=float)

)

hhi = (

    (weights_decimal ** 2).sum()

    if len(weights_decimal)

    else 0

)

effective_holdings = (

    1 / hhi

    if hhi > 0

    else 0

)

entropy = (

    -(weights_decimal * np.log(weights_decimal.replace(0, np.nan)))

    .sum()

    if len(weights_decimal)

    else 0

)

summary_row(

    [

        (

            "HHI",

            f"{hhi:.4f}",

            None,

        ),

        (

            "Effective Holdings",

            f"{effective_holdings:.1f}",

            None,

        ),

        (

            "Portfolio Entropy",

            f"{entropy:.2f}",

            None,

        ),

        (

            "Largest Weight",

            f"{largest_weight:.2f}%",

            None,

        ),

    ]

)

# ==========================================================
# Concentration Diagnostics
# ==========================================================

st.subheader("Concentration Diagnostics")

diagnostics = pd.DataFrame(

    {

        "Metric": [

            "Largest Position",

            "Top 3 Positions",

            "Top 5 Positions",

            "Top 10 Positions",

            "Effective Holdings",

            "Diversification Score",

            "Portfolio Health",

        ],

        "Value": [

            f"{largest_weight:.2f}%",

            f"{top3:.2f}%",

            f"{top5:.2f}%",

            f"{top10:.2f}%",

            f"{effective_holdings:.2f}",

            diversification_score,

            portfolio_health,

        ],

    }

)

holdings_table(

    diagnostics,

)

dataframe_info(

    diagnostics,

)

# ==========================================================
# Drawdown Analysis
# ==========================================================

st.divider()

st.header("Drawdown Analysis")

drawdown_col = first_existing(

    holdings,

    "Drawdown",

    "Max Drawdown",

    "Drawdown %",

)

if drawdown_col:

    drawdowns = numeric_series(

        holdings,

        drawdown_col,

    )

else:

    drawdowns = pd.Series(

        [0.0] * len(holdings),

        dtype=float,

    )

current_drawdown = (

    abs(drawdowns.mean())

    if len(drawdowns)

    else 0

)

maximum_drawdown = (

    abs(drawdowns.min())

    if len(drawdowns)

    else 0

)

average_drawdown = (

    abs(drawdowns.mean())

    if len(drawdowns)

    else 0

)

median_drawdown = (

    abs(drawdowns.median())

    if len(drawdowns)

    else 0

)

drawdown_summary = [

    (

        "Current Drawdown",

        f"{current_drawdown:.2f}%",

        None,

    ),

    (

        "Maximum Drawdown",

        f"{maximum_drawdown:.2f}%",

        None,

    ),

    (

        "Average Drawdown",

        f"{average_drawdown:.2f}%",

        None,

    ),

    (

        "Median Drawdown",

        f"{median_drawdown:.2f}%",

        None,

    ),

]

summary_row(

    drawdown_summary,

)

left_col, right_col = st.columns(
    2,
)

with left_col:

    st.subheader(
        "Drawdown Distribution",
    )

    fig = px.histogram(

        drawdowns,

        nbins=25,

    )

    fig.update_layout(

        height=380,

        xaxis_title="Drawdown (%)",

        yaxis_title="Frequency",

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

with right_col:

    st.subheader(
        "Largest Drawdowns",
    )

    drawdown_table = holdings.copy()

    if drawdown_col:

        drawdown_table = drawdown_table.sort_values(

            drawdown_col,

        )

    holdings_table(

        drawdown_table.head(15),

    )

# ==========================================================
# Value at Risk
# ==========================================================

st.divider()

st.header("Value at Risk (VaR)")

if len(returns):

    confidence_levels = [

        90,

        95,

        99,

    ]

    var_results = []

    for confidence in confidence_levels:

        percentile = 100 - confidence

        value = np.percentile(

            returns,

            percentile,

        )

        var_results.append(

            {

                "Confidence": f"{confidence}%",

                "VaR": value,

            }

        )

    var_df = pd.DataFrame(

        var_results,
        key="var_results",

    )

else:

    var_df = pd.DataFrame()


left_col, right_col = st.columns(
    [
        1,
        2,
    ]
)

with left_col:

    dataframe_info(

        var_df,
    )

    holdings_table(

        var_df,

    )

with right_col:

    if not var_df.empty:

        fig = px.bar(

            var_df,

            x="Confidence",

            y="VaR",

            text="VaR",

            color="VaR",

        )

        fig.update_layout(

            height=360,

            coloraxis_showscale=False,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

# ==========================================================
# Conditional VaR
# ==========================================================

st.subheader(
    "Conditional Value at Risk",
)

cvar_results = []

if len(returns):

    for confidence in [

        90,

        95,

        99,

    ]:

        threshold = np.percentile(

            returns,

            100 - confidence,

        )

        tail = returns[

            returns <= threshold

        ]

        cvar = (

            tail.mean()

            if len(tail)

            else threshold

        )

        cvar_results.append(

            {

                "Confidence": f"{confidence}%",

                "CVaR": cvar,

            }

        )

cvar_df = pd.DataFrame(

    cvar_results,

)

holdings_table(

    cvar_df,
    key="cvar_df",

)

# ==========================================================
# Position Risk Ranking
# ==========================================================

st.divider()

st.header("Position Risk Ranking")

risk_table = holdings.copy()

# Ensure a Risk Score column always exists
risk_table["Risk Score"] = 0.0

# Detect the appropriate weight column
weight_col = next(
    (
        c
        for c in [
            "weight",
            "Weight",
            "target_weight",
            "current_weight",
            "weight_pct",
        ]
        if c in risk_table.columns
    ),
    None,
)

if weight_col is not None and len(returns) == len(risk_table):

    risk_table["Risk Score"] = (
        risk_table[weight_col].abs() * 0.6
        + pd.Series(returns, index=risk_table.index).abs() * 0.4
    )

elif weight_col is not None:

    # Fall back to weight-only score
    risk_table["Risk Score"] = (
        risk_table[weight_col].abs() * 0.6
    )

risk_table = risk_table.sort_values(
    "Risk Score",
    ascending=False,
)

holdings_table(
    risk_table.head(25),
    key="risk_ranking",
)

dataframe_info(
    risk_table,
)

# ==========================================================
# Risk Heatmap
# ==========================================================

st.divider()

st.header("Risk Heatmap")

heatmap_df = holdings.copy()

heatmap_df["Return"] = returns

heatmap_df["Weight"] = weights

if sector_col:

    heatmap_df["Sector"] = holdings[
        sector_col
    ]

else:

    heatmap_df["Sector"] = "Unknown"

fig = px.scatter(

    heatmap_df,

    x="Weight",

    y="Return",

    color="Sector",

    size="Weight",

    hover_name=symbol_col,

    size_max=45,

)

fig.update_layout(

    height=550,

    xaxis_title="Portfolio Weight (%)",

    yaxis_title="Return (%)",

)

st.plotly_chart(

    fig,

    use_container_width=True,

)
# ==========================================================
# Sector Risk Analysis
# ==========================================================

st.divider()

st.header("Sector Risk Analysis")

# Validate required columns
required = {
    "Sector": sector_col,
    "Weight": weight_col,
    "Return": return_col,
}

missing = [
    name
    for name, col in required.items()
    if col is None
    or pd.isna(col)
    or col not in holdings.columns
]

if missing:

    st.info(
        f"Sector Risk Analysis unavailable. Missing column(s): {', '.join(missing)}"
    )

    sector_risk = pd.DataFrame()

else:

    sector_risk = (
        holdings
        .groupby(
            sector_col,
            dropna=False,
        )
        .agg(
            Exposure=(weight_col, "sum"),
            Average_Return=(return_col, "mean"),
        )
        .reset_index()
        .rename(
            columns={
                sector_col: "Sector",
                "Average_Return": "Average Return",
            }
        )
    )

left, right = st.columns(2)

with left:

    st.subheader("Sector Exposure")

    if not sector_risk.empty:

        fig = px.treemap(
            sector_risk,
            path=["Sector"],
            values="Exposure",
            color="Average Return",
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("Sector information unavailable.")

with right:

    st.subheader("Sector Summary")

    holdings_table(
        sector_risk,
        key="sector_risk",
    )

    dataframe_info(
        sector_risk,
    )


# ==========================================================
# Largest Risk Contributors
# ==========================================================

st.divider()

st.header(
    "Largest Risk Contributors",
)

contributors = holdings.copy()

contributors["Risk Contribution"] = (

    weights.abs()

    *

    returns.abs()

)

contributors = contributors.sort_values(

    "Risk Contribution",

    ascending=False,

)

fig = px.bar(

    contributors.head(20),

    x=symbol_col,

    y="Risk Contribution",

    color="Risk Contribution",

    text="Risk Contribution",

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

    contributors.head(20),

)

# ==========================================================
# Open Risk Alerts
# ==========================================================

st.divider()

st.header("Open Risk Alerts")

alerts = []

if largest_weight > 10:

    alerts.append(

        (

            "High Position Concentration",

            f"Largest position is {largest_weight:.2f}%",

            "High",

        )

    )

if top5 > 45:

    alerts.append(

        (

            "Portfolio Concentration",

            f"Top 5 positions represent {top5:.2f}%",

            "Medium",

        )

    )

if maximum_drawdown > 15:

    alerts.append(

        (

            "Large Drawdown",

            f"Maximum drawdown {maximum_drawdown:.2f}%",

            "Critical",

        )

    )

if diversification_score < 60:

    alerts.append(

        (

            "Low Diversification",

            f"Score {diversification_score:.0f}",

            "Medium",

        )

    )

alerts_df = pd.DataFrame(

    alerts,

    columns=[

        "Alert",

        "Description",

        "Severity",

    ],

)

if alerts_df.empty:

    st.success(

        "No active portfolio risk alerts."

    )

else:

    holdings_table(

        alerts_df,
        key="alerts_df",

    )

# ==========================================================
# Historical Risk Trend
# ==========================================================

st.divider()

st.header(
    "Historical Risk Trend",
)

history_file = (

    REPORTS_DIR

    / "history"

    / "risk_history.csv"

)

if history_file.exists():

    history = pd.read_csv(

        history_file,

    )

    date_col = first_existing(

        history,

        "Date",

        "Timestamp",

    )

    score_col = first_existing(

        history,

        "Risk Score",

        "Portfolio Health",

    )

    if date_col and score_col:

        fig = px.line(

            history,

            x=date_col,

            y=score_col,

            markers=True,

        )

        fig.update_layout(

            height=420,

        )

        st.plotly_chart(

            fig,

            use_container_width=True,

        )

        holdings_table(

            history.tail(20),

        )

else:

    st.info(

        "Historical risk data not available."

    )

# ==========================================================
# Stress Testing
# ==========================================================

st.divider()

st.header("Portfolio Stress Testing")

stress_levels = {

    "Market Correction (-5%)": -5,

    "Bear Market (-10%)": -10,

    "Severe Bear (-20%)": -20,

    "Market Crash (-30%)": -30,

}

stress_results = []

for scenario, decline in stress_levels.items():

    estimated_loss = (

        portfolio_value

        * abs(decline)

        / 100

    )

    remaining_value = (

        portfolio_value

        - estimated_loss

    )

    stress_results.append(

        {

            "Scenario": scenario,

            "Shock (%)": decline,

            "Estimated Loss": estimated_loss,

            "Remaining Portfolio": remaining_value,

        }

    )

stress_df = pd.DataFrame(

    stress_results,

)

left, right = st.columns(
    [1, 2]
)

with left:

    holdings_table(

        stress_df,
        key="stress_df",

    )

with right:

    fig = px.bar(

        stress_df,

        x="Scenario",

        y="Estimated Loss",

        color="Estimated Loss",

        text="Estimated Loss",

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
# Portfolio Risk Limits
# ==========================================================

st.divider()

st.header("Portfolio Risk Limits")

limits = pd.DataFrame(

    [

        {

            "Rule": "Maximum Position",

            "Limit": "10%",

            "Current": f"{largest_weight:.2f}%",

            "Status": (

                "PASS"

                if largest_weight <= 10

                else "FAIL"

            ),

        },

        {

            "Rule": "Top 5 Exposure",

            "Limit": "45%",

            "Current": f"{top5:.2f}%",

            "Status": (

                "PASS"

                if top5 <= 45

                else "FAIL"

            ),

        },

        {

            "Rule": "Sector Diversification",

            "Limit": ">= 8",

            "Current": sector_count,

            "Status": (

                "PASS"

                if sector_count >= 8

                else "FAIL"

            ),

        },

        {

            "Rule": "Diversification Score",

            "Limit": ">= 70",

            "Current": diversification_score,

            "Status": (

                "PASS"

                if diversification_score >= 70

                else "FAIL"

            ),

        },

    ]

)

holdings_table(

    limits,

)

# ==========================================================
# Compliance Dashboard
# ==========================================================

st.divider()

st.header("Compliance Summary")

passed = (

    limits["Status"]

    == "PASS"

).sum()

failed = (

    limits["Status"]

    == "FAIL"

).sum()

summary_row(

    [

        (

            "Checks",

            len(limits),

            None,

        ),

        (

            "Passed",

            passed,

            None,

        ),

        (

            "Failed",

            failed,

            None,

        ),

        (

            "Compliance",

            f"{passed/len(limits)*100:.1f}%",

            None,

        ),

    ]

)

st.dataframe(

    limits,

    use_container_width=True,

)

# ==========================================================
# Risk Report Downloads
# ==========================================================

st.divider()

st.header("Risk Reports")

risk_report = CONFIG.risk_file

if risk_report.exists():

    with open(

        risk_report,

        "rb",

    ) as f:

        st.download_button(

            "Download Risk Summary",

            data=f,

            file_name="risk_summary.csv",

            mime="text/csv",

        )

history_report = (

    REPORTS_DIR

    / "history"

    / "risk_history.csv"

)

if history_report.exists():

    with open(

        history_report,

        "rb",

    ) as f:

        st.download_button(

            "Download Risk History",

            data=f,

            file_name="risk_history.csv",

            mime="text/csv",

        )

# ==========================================================
# Diagnostics
# ==========================================================

st.divider()

st.header("Diagnostics")

diagnostics = pd.DataFrame(

    [

        (

            "Portfolio Records",

            len(portfolio),

        ),

        (

            "Holdings",

            len(holdings),

        ),

        (

            "Risk Records",

            len(risk),

        ),

        (

            "Historical Records",

            len(history)

            if "history" in locals()

            else 0,

        ),

        (

            "Portfolio Health",

            portfolio_health,

        ),

        (

            "Diversification Score",

            diversification_score,

        ),

        (

            "Risk Level",

            risk_level,

        ),

    ],

    columns=[

        "Metric",

        "Value",

    ],

)

holdings_table(
    diagnostics,
)

dataframe_info(
    diagnostics,
)

# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(

    "Institutional Scanner Monitor • Risk Dashboard"

)

st.caption(

    "Portfolio Risk • Exposure • Drawdown • VaR • Stress Testing • Compliance"

)