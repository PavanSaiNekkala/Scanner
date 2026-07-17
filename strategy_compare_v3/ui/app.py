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



from strategy_compare_v4.derived_metrics.derived_engine import (
    DerivedMetricsEngine
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

    "derived_metrics",

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
        # STEP 1
        # --------------------------------------------------


        status.info(

            "Step 1/9 : Data Profiling"

        )



        profiler = DataProfiler(

            df

        )



        st.session_state["profile"] = (

            profiler.generate()

        )



        progress.progress(11)





        # --------------------------------------------------
        # STEP 2
        # --------------------------------------------------


        status.info(

            "Step 2/9 : Relationship Analysis"

        )



        relationship_engine = RelationshipEngine(

            df

        )



        st.session_state["relationships"] = (

            relationship_engine.generate()

        )



        progress.progress(22)





        # --------------------------------------------------
        # STEP 3
        # --------------------------------------------------


        status.info(

            "Step 3/9 : Derived Metrics"

        )



        derived_engine = DerivedMetricsEngine(

            df

        )



        derived_df = derived_engine.run()



        st.session_state["derived_metrics"] = derived_df



        progress.progress(33)





        # --------------------------------------------------
        # STEP 4
        # --------------------------------------------------


        status.info(

            "Step 4/9 : Feature Engineering"

        )



        feature_engine = FeatureEngine(

            derived_df

        )



        feature_df = feature_engine.run()



        st.session_state["features"] = feature_df



        progress.progress(44)

    
        # --------------------------------------------------
        # STEP 5
        # --------------------------------------------------


        status.info(

            "Step 5/9 : Normalization"

        )



        normalization_engine = NormalizationEngine(

            feature_df

        )



        normalized = normalization_engine.run()



        st.session_state["normalized"] = normalized



        analysis_df = normalized[

            "Percentile"

        ]



        progress.progress(55)





        # --------------------------------------------------
        # STEP 6
        # --------------------------------------------------


        status.info(

            "Step 6/9 : Institutional Scoring"

        )



        scoring_engine = ScoringEngine(

            analysis_df

        )



        scored = scoring_engine.run()



        st.session_state["scores"] = scored



        progress.progress(66)





        # --------------------------------------------------
        # STEP 7
        # --------------------------------------------------


        status.info(

            "Step 7/9 : Recommendations"

        )



        recommendation_engine = RecommendationEngine(

            scored

        )



        recommended = recommendation_engine.generate()



        st.session_state["recommendations"] = recommended



        progress.progress(77)





        # --------------------------------------------------
        # STEP 8
        # --------------------------------------------------


        status.info(

            "Step 8/9 : Optimization"

        )



        try:


            optimization_engine = OptimizationEngine(

                recommended

            )


            optimization = optimization_engine.run()



        except TypeError:


            optimization = {}



        st.session_state["optimization"] = optimization



        progress.progress(88)





        # --------------------------------------------------
        # STEP 9
        # --------------------------------------------------


        status.info(

            "Step 9/9 : Reports"

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
    Convert objects into Streamlit compatible format.
    Prevents Arrow conversion errors.
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


    tab1, tab2, tab3, tab4, tab5 = st.tabs(

        [

            "Recommendations",

            "Charts",

            "Profiling",

            "Relationships",

            "Derived Metrics"

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





    # ======================================================
    # TAB 5 : DERIVED METRICS
    # ======================================================


    with tab5:


        derived = st.session_state["derived_metrics"]



        if derived is not None:


            display_dataframe(

                "Strategy Derived Metrics",

                derived

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