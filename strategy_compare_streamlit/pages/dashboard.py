"""
Main Dashboard
"""

import copy

import streamlit as st

import pandas as pd

from pages.executive import ExecutivePage

from pages.ranking import RankingPage

from pages.comparison import ComparisonPage

from pages.analytics import AnalyticsPage

from pages.downloads import DownloadPage


###########################################################################
# DASHBOARD
###########################################################################

class DashboardPage:

    def __init__(

        self,

        result

    ):

        self.result = result

        self.original = result[

            "ranked"

        ].copy()

        self.filtered = self.original.copy()

        self.session()

    ###########################################################################
    # SESSION STATE
    ###########################################################################

    def session(

        self

    ):

        defaults = {

            "dashboard_search": "",

            "dashboard_grade": [],

            "dashboard_recommendation": [],

            "dashboard_min_score": 0.0,

            "dashboard_max_score": 100.0

        }

        for key, value in defaults.items():

            if key not in st.session_state:

                st.session_state[

                    key

                ] = value

    ###########################################################################
    # PAGE
    ###########################################################################

    def render(

        self

    ):

        st.title(

            "Institutional Strategy Comparison Dashboard"

        )

        st.caption(

            "Institutional Strategy Evaluation & Analytics"

        )

        self.sidebar()

        self.apply_filters()

        if self.filtered.empty:

            st.warning(

                "No strategies match the selected filters."

            )

            return

        self.kpis()

        st.divider()

        self.build_tabs()

    ###########################################################################
    # SIDEBAR
    ###########################################################################

    def sidebar(

        self

    ):

        st.sidebar.header(

            "Global Filters"

        )

        st.session_state[

            "dashboard_search"

        ] = st.sidebar.text_input(

            "Search Strategy",

            value=st.session_state[

                "dashboard_search"

            ]

        )

        grades = sorted(

            self.original[

                "Grade"

            ]

            .dropna()

            .unique()

            .tolist()

        )

        st.session_state[

            "dashboard_grade"

        ] = st.sidebar.multiselect(

            "Grade",

            grades,

            default=grades

        )

        recommendations = sorted(

            self.original[

                "Recommendation"

            ]

            .dropna()

            .unique()

            .tolist()

        )

        st.session_state[

            "dashboard_recommendation"

        ] = st.sidebar.multiselect(

            "Recommendation",

            recommendations,

            default=recommendations

        )

        minimum = float(

            self.original[

                "Overall Score"

            ].min()

        )

        maximum = float(

            self.original[

                "Overall Score"

            ].max()

        )

        score = st.sidebar.slider(

            "Overall Score",

            minimum,

            maximum,

            (

                st.session_state[

                    "dashboard_min_score"

                ],

                st.session_state[

                    "dashboard_max_score"

                ]

            )

        )

        st.session_state[

            "dashboard_min_score"

        ] = score[0]

        st.session_state[

            "dashboard_max_score"

        ] = score[1]

        st.sidebar.divider()

        if st.sidebar.button(

            "Reset Filters",

            width="stretch"

        ):

            st.session_state[

                "dashboard_search"

            ] = ""

            st.session_state[

                "dashboard_grade"

            ] = grades

            st.session_state[

                "dashboard_recommendation"

            ] = recommendations

            st.session_state[

                "dashboard_min_score"

            ] = minimum

            st.session_state[

                "dashboard_max_score"

            ] = maximum

            st.rerun()

    ###########################################################################
    # APPLY FILTERS
    ###########################################################################

    def apply_filters(

        self

    ):

        dataframe = self.original.copy()

        search = st.session_state[

            "dashboard_search"

        ]

        if search:

            dataframe = dataframe[

                dataframe[

                    "Strategy"

                ]

                .str.contains(

                    search,

                    case=False,

                    na=False

                )

            ]

        grades = st.session_state[

            "dashboard_grade"

        ]

        if grades:

            dataframe = dataframe[

                dataframe[

                    "Grade"

                ]

                .isin(

                    grades

                )

            ]

        recommendations = st.session_state[

            "dashboard_recommendation"

        ]

        if recommendations:

            dataframe = dataframe[

                dataframe[

                    "Recommendation"

                ]

                .isin(

                    recommendations

                )

            ]

        dataframe = dataframe[

            (

                dataframe[

                    "Overall Score"

                ]

                >=

                st.session_state[

                    "dashboard_min_score"

                ]

            )

            &

            (

                dataframe[

                    "Overall Score"

                ]

                <=

                st.session_state[

                    "dashboard_max_score"

                ]

            )

        ]

        self.filtered = dataframe.reset_index(

            drop=True

        )

    ###########################################################################
    # KPI CARDS
    ###########################################################################

    def kpis(

        self

    ):

        best = self.filtered.iloc[

            0

        ]

        col1, col2, col3, col4 = st.columns(

            4

        )

        col1.metric(

            "Strategies",

            len(

                self.filtered

            )

        )

        col2.metric(

            "Top Strategy",

            best[

                "Strategy"

            ]

        )

        col3.metric(

            "Highest Score",

            round(

                self.filtered[

                    "Overall Score"

                ].max(),

                2

            )

        )

        col4.metric(

            "Average Score",

            round(

                self.filtered[

                    "Overall Score"

                ].mean(),

                2

            )

        )

    ###########################################################################
    # DASHBOARD SUMMARY
    ###########################################################################

    def summary(

        self

    ):

        st.subheader(

            "Portfolio Summary"

        )

        summary = pd.DataFrame({

            "Metric": [

                "Strategies",

                "Highest Score",

                "Average Score",

                "Lowest Score",

                "Strong Buy",

                "Buy",

                "Watch"

            ],

            "Value": [

                len(

                    self.filtered

                ),

                round(

                    self.filtered[

                        "Overall Score"

                    ].max(),

                    2

                ),

                round(

                    self.filtered[

                        "Overall Score"

                    ].mean(),

                    2

                ),

                round(

                    self.filtered[

                        "Overall Score"

                    ].min(),

                    2

                ),

                int(

                    (

                        self.filtered[

                            "Recommendation"

                        ]

                        ==

                        "Strong Buy"

                    ).sum()

                ),

                int(

                    (

                        self.filtered[

                            "Recommendation"

                        ]

                        ==

                        "Buy"

                    ).sum()

                ),

                int(

                    (

                        self.filtered[

                            "Recommendation"

                        ]

                        ==

                        "Watch"

                    ).sum()

                )

            ]

        })

        summary = summary.astype(

            str

        )

        st.dataframe(

            summary,

            width="stretch",

            hide_index=True

        )

    ###########################################################################
    # BUILD FILTERED RESULT
    ###########################################################################

    def filtered_result(

        self

    ):

        result = copy.deepcopy(

            self.result

        )

        result[

            "ranked"

        ] = self.filtered.copy()

        return result

    ###########################################################################
    # BUILD TABS
    ###########################################################################

    def build_tabs(

        self

    ):

        self.summary()

        st.divider()

        result = self.filtered_result()

        tabs = st.tabs(

            [

                "Executive",

                "Ranking",

                "Comparison",

                "Analytics",

                "Downloads"

            ]

        )

        with tabs[

            0

        ]:

            self.executive_tab(

                result

            )

        with tabs[

            1

        ]:

            self.ranking_tab(

                result

            )

        with tabs[

            2

        ]:

            self.comparison_tab(

                result

            )

        with tabs[

            3

        ]:

            self.analytics_tab(

                result

            )

        with tabs[

            4

        ]:

            self.downloads_tab(

                result

            )

    ###########################################################################
    # EXECUTIVE TAB
    ###########################################################################

    def executive_tab(

        self,

        result

    ):

        try:

            page = ExecutivePage(

                result

            )

            page.render()

        except Exception as error:

            st.error(

                f"Executive page failed: {error}"

            )

    ###########################################################################
    # RANKING TAB
    ###########################################################################

    def ranking_tab(

        self,

        result

    ):

        try:

            page = RankingPage(

                result

            )

            page.render()

        except Exception as error:

            st.error(

                f"Ranking page failed: {error}"

            )

    ###########################################################################
    # COMPARISON TAB
    ###########################################################################

    def comparison_tab(

        self,

        result

    ):

        try:

            page = ComparisonPage(

                result

            )

            page.render()

        except Exception as error:

            st.error(

                f"Comparison page failed: {error}"

            )

    ###########################################################################
    # ANALYTICS TAB
    ###########################################################################

    def analytics_tab(

        self,

        result

    ):

        try:

            page = AnalyticsPage(

                result

            )

            page.render()

        except Exception as error:

            st.error(

                f"Analytics page failed: {error}"

            )

    ###########################################################################
    # DOWNLOADS TAB
    ###########################################################################

    def downloads_tab(

        self,

        result

    ):

        try:

            page = DownloadPage(

                result

            )

            page.render()

        except Exception as error:

            st.error(

                f"Downloads page failed: {error}"

            )

    ###########################################################################
    # REFRESH DASHBOARD
    ###########################################################################

    def refresh(

        self

    ):

        col1, col2 = st.columns(

            [

                1,

                5

            ]

        )

        with col1:

            if st.button(

                "🔄 Refresh",

                width="stretch"

            ):

                st.rerun()

        with col2:

            st.caption(

                "Refresh the dashboard after generating a new comparison report."

            )

    ###########################################################################
    # ABOUT
    ###########################################################################

    def about(

        self

    ):

        st.divider()

        with st.expander(

            "About Dashboard",

            expanded=False

        ):

            rows = [

                {

                    "Property":

                        "Application",

                    "Value":

                        "Institutional Strategy Comparison Dashboard"

                },

                {

                    "Property":

                        "Version",

                    "Value":

                        "3.0"

                },

                {

                    "Property":

                        "Framework",

                    "Value":

                        "Streamlit"

                },

                {

                    "Property":

                        "Analytics Engine",

                    "Value":

                        "Institutional Quant V3"

                },

                {

                    "Property":

                        "Ranking Engine",

                    "Value":

                        "Weighted Multi-Factor"

                },

                {

                    "Property":

                        "Visualization",

                    "Value":

                        "Plotly"

                },

                {

                    "Property":

                        "Export Formats",

                    "Value":

                        "Excel / CSV / JSON"

                }

            ]

            dataframe = pd.DataFrame(

                rows

            )

            dataframe = dataframe.astype(

                str

            )

            st.dataframe(

                dataframe,

                width="stretch",

                hide_index=True

            )

    ###########################################################################
    # FOOTER
    ###########################################################################

    def footer(

        self

    ):

        st.divider()

        st.caption(

            "© 2026 Institutional Strategy Comparison Dashboard • Version 3.0"
        )

    ###########################################################################
    # COMPLETE PAGE
    ###########################################################################

    def render(

        self

    ):

        st.title(

            "Institutional Strategy Comparison Dashboard"

        )

        st.caption(

            "Comprehensive Strategy Evaluation, Ranking, Analytics & Reporting"

        )

        self.sidebar()

        self.apply_filters()

        if self.filtered.empty:

            st.warning(

                "No strategies match the selected filters."

            )

            return

        self.refresh()

        st.divider()

        self.kpis()

        st.divider()

        self.build_tabs()

        self.about()

        self.footer()