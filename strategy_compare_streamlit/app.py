"""
Institutional Strategy Comparison Dashboard
Version 3.0
"""

import streamlit as st

import pandas as pd

from config import OUTPUTS

from pipeline import StrategyPipeline

from pages.dashboard import DashboardPage

###########################################################################
# PAGE CONFIGURATION
###########################################################################

st.set_page_config(
    page_title="Institutional Strategy Comparison",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

###########################################################################
# APPLICATION HEADER
###########################################################################

st.title("📈 Institutional Strategy Comparison Dashboard")

st.caption(
    "Institutional-grade strategy evaluation, comparison, analytics and reporting."
)

st.info("""
### Usage

• Upload one or more **Output*.xlsx** strategy reports.

• If no files are uploaded, reports will automatically be loaded from the project's **outputs/** folder.

• Click **Generate Comparison** to execute the complete institutional pipeline.

Supported exports include:

- Executive Dashboard
- Strategy Ranking
- Strategy Comparison
- Analytics Dashboard
- Download Center
""")

###########################################################################
# SIDEBAR
###########################################################################

st.sidebar.header("Execution")

generate = st.sidebar.button("🚀 Generate Comparison", width="stretch")

###########################################################################
# LOCAL REPORTS
###########################################################################

local_reports = sorted(OUTPUTS.glob("Output*.xlsx"))

###########################################################################
# OPTIONAL FILE UPLOAD
###########################################################################

uploaded_reports = st.file_uploader(
    "Optional: Upload Strategy Reports", type=["xlsx"], accept_multiple_files=True
)

###########################################################################
# SAVE UPLOADED REPORTS
###########################################################################


def save_uploaded_reports(files):
    if not files:
        return

    for report in OUTPUTS.glob("*.xlsx"):
        report.unlink()

    for report in files:
        with open(OUTPUTS / report.name, "wb") as file:
            file.write(report.getbuffer())


###########################################################################
# EXECUTE PIPELINE
###########################################################################

if generate:
    #######################################################################
    # Uploaded reports override local reports
    #######################################################################

    if uploaded_reports:
        save_uploaded_reports(uploaded_reports)

        local_reports = sorted(OUTPUTS.glob("Output*.xlsx"))

    #######################################################################
    # VALIDATION
    #######################################################################

    if len(local_reports) < 2:
        st.error("""
At least two strategy reports are required.

Either

• Upload two or more Output*.xlsx files

or

• Place them inside the outputs/ directory.
""")

        st.stop()

    #######################################################################
    # PIPELINE
    #######################################################################

    progress = st.progress(0)

    status = st.empty()

    try:
        status.info("Loading strategy reports...")

        progress.progress(20)

        with st.spinner("Executing institutional pipeline..."):
            pipeline = StrategyPipeline(OUTPUTS)

            status.info("Building strategy statistics...")

            progress.progress(40)

            result = pipeline.execute()

            status.info("Generating rankings...")

            progress.progress(70)

            st.session_state["result"] = result

            status.info("Preparing dashboard...")

            progress.progress(90)

        progress.progress(100)

        status.success("Strategy comparison completed successfully.")

    except Exception as error:
        progress.empty()

        status.empty()

        st.exception(error)

        st.stop()

###########################################################################
# SESSION RESTORE
###########################################################################

if "result" not in st.session_state:
    st.warning("""
No comparison has been generated.

Click **Generate Comparison** to start the institutional
strategy evaluation pipeline.
""")

    st.stop()

###########################################################################
# PIPELINE RESULT
###########################################################################

result = st.session_state["result"]

ranked = result["ranked"]

recommendations = result["recommendations"]

overlap = result["overlap"]

###########################################################################
# EXECUTION SUMMARY
###########################################################################

st.success("Institutional comparison completed successfully.")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Strategies", len(ranked))

col2.metric("Recommendations", len(recommendations))

col3.metric("Overlap Rows", len(overlap))

col4.metric("Best Strategy", ranked.iloc[0]["Strategy"])

###########################################################################
# REPORT INFORMATION
###########################################################################

with st.expander("Pipeline Summary", expanded=False):
    summary = [
        {"Property": "Reports Loaded", "Value": len(local_reports)},
        {"Property": "Strategies Ranked", "Value": len(ranked)},
        {"Property": "Best Strategy", "Value": ranked.iloc[0]["Strategy"]},
        {"Property": "Highest Score", "Value": round(ranked["Overall Score"].max(), 2)},
        {
            "Property": "Average Score",
            "Value": round(ranked["Overall Score"].mean(), 2),
        },
    ]

    dataframe = pd.DataFrame(summary)

    dataframe = dataframe.astype(str)

    st.dataframe(dataframe, width="stretch", hide_index=True)

###########################################################################
# DASHBOARD
###########################################################################

st.divider()

DashboardPage(result).render()

###########################################################################
# APPLICATION FOOTER
###########################################################################

st.divider()

left, center, right = st.columns([2, 3, 2])

with left:
    st.caption("Institutional Strategy Comparison Dashboard")

with center:
    st.caption("Version 3.0 • Production Release")

with right:
    st.caption("Powered by Streamlit")

###########################################################################
# ABOUT
###########################################################################

with st.expander("About", expanded=False):
    about = [
        {
            "Property": "Application",
            "Value": "Institutional Strategy Comparison Dashboard",
        },
        {"Property": "Version", "Value": "3.0"},
        {"Property": "Architecture", "Value": "Modular V3"},
        {"Property": "Pipeline", "Value": "StrategyPipeline"},
        {"Property": "Dashboard", "Value": "DashboardPage"},
        {"Property": "Analytics", "Value": "ChartEngine"},
        {"Property": "Ranking", "Value": "Weighted Multi-Factor"},
        {"Property": "Reports", "Value": "Excel / CSV / JSON"},
        {"Property": "Technology", "Value": "Python • Pandas • Plotly • Streamlit"},
    ]

    dataframe = pd.DataFrame(about)

    dataframe = dataframe.astype(str)

    st.dataframe(dataframe, width="stretch", hide_index=True)

###########################################################################
# APPLICATION INFORMATION
###########################################################################

st.caption("""
This application automatically evaluates multiple institutional trading
strategies, generates weighted rankings, executive insights,
comparative analytics, visual dashboards and downloadable reports
through a fully modular production-ready architecture.
""")
