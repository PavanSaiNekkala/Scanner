"""
============================================================
Institutional Strategy Comparison Engine V3

Main Streamlit Application

Author : Pavan Sai

============================================================
"""

from __future__ import annotations

import traceback

import streamlit as st
import pandas as pd

from core.loader import DataLoader

from profiling.profiler import DataProfiler

from relationships.relationship_engine import (
    RelationshipEngine
)

from feature_engineering.feature_engine import (
    FeatureEngine
)

from normalization.normalization_engine import (
    NormalizationEngine
)

from scoring.scoring_engine import (
    ScoringEngine
)

from recommendation.recommendation_engine import (
    RecommendationEngine
)

from optimization.optimization_engine import (
    OptimizationEngine
)

from visualization.dashboards import (
    DashboardEngine
)

from reports.report_engine import (
    ReportEngine
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="Institutional Strategy Engine",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULT_KEYS = [

    "dataframe",

    "metadata",

    "profile",

    "relationships",

    "features",

    "normalized",

    "scores",

    "recommendations",

    "optimization",

    "reports",

]

for key in DEFAULT_KEYS:

    if key not in st.session_state:

        st.session_state[key] = None

# ==========================================================
# HEADER
# ==========================================================

st.title(

    "Institutional Strategy Comparison Engine V3"

)

st.caption(

    "Professional Quantitative Strategy Analytics Platform"

)

st.divider()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header(

    "Data Source"

)

uploaded_file = st.sidebar.file_uploader(

    "Upload CSV / Excel",

    type=[

        "csv",

        "xlsx",

        "xls"

    ]

)

# ==========================================================
# LOAD DATA
# ==========================================================

if uploaded_file is not None:

    try:

        loader = DataLoader(

            uploaded_file

        )

        dataframe = loader.run()

        st.session_state["dataframe"] = dataframe

        st.session_state["metadata"] = loader.get_metadata()

        st.success(

            f"Loaded "

            f"{len(dataframe):,} rows × "

            f"{len(dataframe.columns)} columns."

        )

        with st.expander(

            "Dataset Metadata",

            expanded=False

        ):

            st.json(

                loader.get_metadata()

            )

    except Exception as exc:

        st.error(

            f"Dataset loading failed\n\n{exc}"

        )

        st.code(

            traceback.format_exc()

        )

        st.stop()

else:

    st.info(

        "Upload a CSV or Excel strategy report to begin."

    )

    st.stop()

# ==========================================================
# ANALYSIS BUTTON
# ==========================================================

run_analysis = st.sidebar.button(

    "Run Complete Analysis",

    use_container_width=True

)

# ==========================================================
# EXECUTION
# ==========================================================

if run_analysis:

    progress = st.progress(0)

    status = st.empty()

    df = st.session_state["dataframe"]

    try:

        # --------------------------------------------------

        status.info(

            "Step 1/8 : Data Profiling"

        )

        profiler = DataProfiler(df)

        st.session_state["profile"] = (

            profiler.run()

        )

        progress.progress(12)

        # --------------------------------------------------

        status.info(

            "Step 2/8 : Relationship Analysis"

        )

        relationship_engine = RelationshipEngine(

            df

        )

        st.session_state["relationships"] = (

            relationship_engine.run()

        )

        progress.progress(25)

        # --------------------------------------------------

        status.info(

            "Step 3/8 : Feature Engineering"

        )

        feature_engine = FeatureEngine(

            df

        )

        feature_df = feature_engine.run()

        st.session_state["features"] = feature_df

        progress.progress(38)

        # --------------------------------------------------

        status.info(

            "Step 4/8 : Normalization"

        )

        normalization_engine = (

            NormalizationEngine(

                feature_df

            )

        )

        normalized = (

            normalization_engine.run()

        )

        st.session_state["normalized"] = normalized

        analysis_df = normalized["Percentile"]

        progress.progress(50)

        # --------------------------------------------------

        status.info(

            "Step 5/8 : Institutional Scoring"

        )

        scoring_engine = ScoringEngine(

            analysis_df

        )

        scored = scoring_engine.run()

        st.session_state["scores"] = scored

        progress.progress(62)

        # --------------------------------------------------

        status.info(

            "Step 6/8 : Recommendations"

        )

        recommendation_engine = RecommendationEngine(

            scored

        )

        recommended = recommendation_engine.generate()

        st.session_state["recommendations"] = recommended

        progress.progress(75)

        # --------------------------------------------------

        status.info(

            "Step 7/8 : Optimization"

        )

        try:

            optimization_engine = OptimizationEngine(

                recommended

            )

            optimization = optimization_engine.run()

        except TypeError:

            # Engine may require additional arguments

            optimization = {}

        st.session_state["optimization"] = optimization

        progress.progress(87)

        # --------------------------------------------------

        status.info(

            "Step 8/8 : Reports"

        )

        report_engine = ReportEngine(

            recommended

        )

        reports = report_engine.run()

        st.session_state["reports"] = reports

        progress.progress(100)

        status.success(

            "Analysis Completed Successfully."

        )

    except Exception as exc:

        st.error(

            f"Analysis failed\n\n{exc}"

        )

        st.code(

            traceback.format_exc()

        )

        st.stop()

# ==========================================================
# STREAMLIT SAFE DISPLAY HELPERS
# ==========================================================


def make_streamlit_safe(data):

    """
    Convert DataFrames into Arrow compatible format.
    Prevents Streamlit conversion failures.
    """

    if isinstance(
        data,
        pd.DataFrame
    ):

        df = data.copy()


        for column in df.columns:


            if df[column].dtype == "object":


                df[column] = (

                    df[column]

                    .astype(str)

                )


        return df


    return data



def display_dataframe(
    title,
    data
):

    """
    Universal renderer.

    Supports:

    DataFrame
    Dictionary of DataFrames
    Normal objects

    """


    st.subheader(title)



    # ----------------------------------------------
    # DataFrame
    # ----------------------------------------------

    if isinstance(

        data,

        pd.DataFrame

    ):


        st.dataframe(

            make_streamlit_safe(data),

            width="stretch"

        )


        return



    # ----------------------------------------------
    # Dictionary
    # ----------------------------------------------

    if isinstance(

        data,

        dict

    ):


        for name, value in data.items():


            st.markdown(

                f"### {name}"

            )


            display_dataframe(

                name,

                value

            )


        return



    # ----------------------------------------------
    # Other Objects
    # ----------------------------------------------

    st.write(data)

# ==========================================================
# DISPLAY RESULTS
# ==========================================================


if st.session_state["recommendations"] is not None:


    recommended = st.session_state["recommendations"]


    st.divider()


    st.header(

        "Analysis Results"

    )



    # ------------------------------------------------------
    # SUMMARY METRICS
    # ------------------------------------------------------


    metric1, metric2, metric3, metric4 = st.columns(4)



    metric1.metric(

        "Strategies",

        len(recommended)

    )


    metric2.metric(

        "Columns",

        len(recommended.columns)

    )



    if "Composite Score" in recommended.columns:


        metric3.metric(

            "Average Score",

            round(

                recommended["Composite Score"]

                .mean(),

                2

            )

        )



        metric4.metric(

            "Maximum Score",

            round(

                recommended["Composite Score"]

                .max(),

                2

            )

        )



    # ------------------------------------------------------
    # TABS
    # ------------------------------------------------------


    tab1, tab2, tab3, tab4 = st.tabs(

        [

            "Recommendations",

            "Charts",

            "Profiling",

            "Relationships"

        ]

    )



    # ======================================================
    # TAB 1 : RECOMMENDATIONS
    # ======================================================


    with tab1:


        display_dataframe(

            "Top Strategies",

            recommended

        )



    # ======================================================
    # TAB 2 : CHARTS
    # ======================================================


    with tab2:


        if "Recommendation" in recommended.columns:


            st.subheader(

                "Recommendation Distribution"

            )


            st.bar_chart(

                recommended[

                    "Recommendation"

                ]

                .value_counts()

            )



        if "Composite Score" in recommended.columns:


            st.subheader(

                "Composite Score Distribution"

            )


            chart_data = (

                recommended

                .sort_values(

                    "Composite Score"

                )

                [

                    "Composite Score"

                ]

            )


            st.line_chart(

                chart_data

            )

    # ======================================================
    # TAB 3 : PROFILING
    # ======================================================


    with tab3:


        profile = st.session_state["profile"]


        if profile is not None:


            display_dataframe(

                "Dataset Profiling",

                profile

            )



    # ======================================================
    # TAB 4 : RELATIONSHIPS
    # ======================================================


    with tab4:


        relationships = st.session_state["relationships"]


        if relationships is not None:


            display_dataframe(

                "Relationship Analysis",

                relationships

            )



# ==========================================================
# DOWNLOAD REPORT
# ==========================================================


reports = st.session_state["reports"]


if reports is not None:


    excel_file = reports.get(

        "Excel File"

    )


    if excel_file:


        with open(

            excel_file,

            "rb"

        ) as file:


            st.download_button(

                label=(

                    "Download Institutional Report"

                ),

                data=file,

                file_name=(

                    "Institutional_Report.xlsx"

                ),

                mime=(

                    "application/vnd.openxmlformats-officedocument."

                    "spreadsheetml.sheet"

                ),

                width="stretch"

            )



# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(

    "Institutional Strategy Comparison Engine V3 | "

    "Professional Quantitative Analytics Platform"
)