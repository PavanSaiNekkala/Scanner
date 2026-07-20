"""
Sidebar Component
=================

Reusable sidebar for the Institutional Strategy Comparison Platform.
"""

from pathlib import Path

import streamlit as st


def render_sidebar() -> None:
    """Render the application sidebar."""

    with st.sidebar:
        st.title("📊 Strategy Platform")

        st.caption("Institutional Strategy Comparison v4")

        st.divider()

        st.subheader("Navigation")

        st.markdown("""
🏠 Home

📂 Data Load

📈 Strategies

🏢 Stocks

🏆 Leaderboards

💼 Portfolio

🛡 Robustness

🔗 Correlation

📄 Reports

⚙ Settings
""")

        st.divider()

        st.subheader("Project")

        st.write("Version")
        st.success("v4.0")

        st.write("Author")
        st.info("Pavan Sai Nekkala")

        st.divider()

        st.subheader("Current Status")

        if st.session_state.get("reports_loaded", False):
            st.success("Reports Loaded")

        else:
            st.warning("Reports Not Loaded")

        output = st.session_state.get("output_folder")

        if output is None:
            st.info("Output Folder : Not Selected")

        else:
            st.success(Path(output).name)

        st.divider()

        st.subheader("Quick Statistics")

        strategy_df = st.session_state.get("strategy_df")
        stock_df = st.session_state.get("stock_df")
        portfolio_df = st.session_state.get("portfolio_df")

        strategies = strategy_df["Strategy"].nunique() if strategy_df is not None else 0

        stocks = stock_df["Stock"].nunique() if stock_df is not None else 0

        portfolio = len(portfolio_df) if portfolio_df is not None else 0

        st.metric("Strategies", strategies)

        st.metric("Stocks", stocks)

        st.metric("Portfolio", portfolio)

        st.divider()

        st.caption("© 2026 Institutional Strategy Analytics Platform")
