"""
Plotly Theme
"""

import plotly.io as pio

from .colors import CHART_COLORS


def apply_plotly_theme():

    template = pio.templates["plotly_white"]

    template.layout.colorway = CHART_COLORS

    template.layout.font.family = "Arial"

    template.layout.margin = dict(
        l=20,
        r=20,
        t=50,
        b=20,
    )

    template.layout.paper_bgcolor = "white"

    template.layout.plot_bgcolor = "white"

    pio.templates.default = template
