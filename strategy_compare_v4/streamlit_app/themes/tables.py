"""
DataFrame Styling
"""

import pandas as pd


def style_dataframe(
    df: pd.DataFrame,
):

    return df.style.hide(axis="index").format(precision=2)
