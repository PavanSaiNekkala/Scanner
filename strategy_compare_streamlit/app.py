"""
Strategy Comparison Dashboard
"""

from pathlib import Path

import streamlit as st

from config import OUTPUTS

from pipeline import StrategyPipeline

from pages.executive import ExecutivePage
from pages.ranking import RankingPage
from pages.comparison import ComparisonPage
from pages.analytics import AnalyticsPage
from pages.downloads import DownloadPage


###########################################################################
# PAGE CONFIG
###########################################################################

st.set_page_config(

    page_title="Strategy Comparison Dashboard",

    page_icon="📈",

    layout="wide"

)

###########################################################################
# TITLE
###########################################################################

st.title(

    "📈 Strategy Comparison Dashboard"

)

st.markdown(

    "Automatically loads reports from the outputs folder. "
    "You can also upload reports manually if required."

)

st.info(
    """
    **Usage Instructions**

    • Upload one or more strategy report Excel files (`.xlsx`) and click **Generate Comparison**.

    • If no files are uploaded, simply click **Generate Comparison**. The application will automatically load all available `Output*.xlsx` files from the project's **`outputs/`** directory and generate the comparison dashboard and consolidated Excel report.
    """
)

###########################################################################
# SIDEBAR
###########################################################################

st.sidebar.header(

    "Settings"

)

run = st.sidebar.button(

    "Generate Comparison"

)

###########################################################################
# LOCAL REPORTS
###########################################################################

local_reports = sorted(

    OUTPUTS.glob(

        "Output*.xlsx"

    )

)

###########################################################################
# OPTIONAL UPLOAD
###########################################################################

uploaded = st.file_uploader(

    "Optional: Upload Strategy Reports",

    type=["xlsx"],

    accept_multiple_files=True

)

###########################################################################
# SAVE UPLOADED FILES
###########################################################################

def save_uploaded(files):

    if not files:

        return

    for file in OUTPUTS.glob(

        "*.xlsx"

    ):

        file.unlink()

    for file in files:

        with open(

            OUTPUTS / file.name,

            "wb"

        ) as f:

            f.write(

                file.getbuffer()

            )

###########################################################################
# EXECUTION
###########################################################################

if run:

    #######################################################################
    # Uploaded files take priority
    #######################################################################

    if uploaded:

        save_uploaded(

            uploaded

        )

        local_reports = sorted(

            OUTPUTS.glob(

                "Output*.xlsx"

            )

        )

    #######################################################################
    # Validation
    #######################################################################

    if len(local_reports) < 2:

        st.error(

            "No strategy reports found in outputs/.\n\n"
            "Either place your Output*.xlsx reports in the outputs folder "
            "or upload them manually."

        )

        st.stop()

    progress = st.progress(

        0

    )

    message = st.empty()

    message.info(

        "Loading strategy reports..."

    )

    progress.progress(

        20

    )

    try:

        pipeline = StrategyPipeline(

            OUTPUTS

        )

        result = pipeline.execute()

        st.write(

            "### Pipeline Result"

        )

        st.write(

            result.keys()

        )

        st.write(

            "Ranked Shape"

        )

        st.write(

            result["ranked"].shape

        )

        st.write(

            result["ranked"].head()

        )
        
        st.session_state["result"] = result

    except Exception as e:

        st.exception(

            e

        )

        st.stop()

    progress.progress(

        100

    )

    message.success(

        "Comparison completed successfully."

    )

if "result" in st.session_state:

    st.write(

        "### Ranked"

    )

    st.dataframe(

        st.session_state["result"]["ranked"],

        width="stretch"

    )

    st.write(

        "### Recommendations"

    )

    st.dataframe(

        st.session_state["result"]["recommendations"],

        width="stretch"

    )

    st.write(

        "### Overlap"

    )

    st.dataframe(

        st.session_state["result"]["overlap"],

        width="stretch"

    )

###########################################################################
# DASHBOARD
###########################################################################

if "result" in st.session_state:

    result = st.session_state["result"]

    st.success(

        "Comparison Generated Successfully"

    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(

        [

            "Executive",

            "Ranking",

            "Comparison",

            "Analytics",

            "Downloads"

        ]

    )

    with tab1:

        ExecutivePage(

            result

        ).render()

    with tab2:

        RankingPage(

            result

        ).render()

    with tab3:

        ComparisonPage(

            result

        ).render()

    with tab4:

        AnalyticsPage(

            result

        ).render()

    with tab5:

        DownloadPage(

            result

        ).render()