"""
Institutional Theme
"""

from .charts import apply_plotly_theme
from .css import load_css


def apply_theme():
    """
    Apply the global application theme.
    """

    load_css()

    apply_plotly_theme()
