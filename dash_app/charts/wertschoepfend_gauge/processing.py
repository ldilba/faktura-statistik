from typing import Tuple, Dict, Any

import plotly.graph_objects as go
import pandas as pd

from common import data
from common.constants import GAUGE_MARGINS


def create_gauge_chart(
    df_grouped: pd.DataFrame, faktura_target: float
) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Erzeugt einen Gauge-Chart, der die kumulative wertschöpfende Stunden (in PT) anzeigt.
    """
    total_value = df_grouped["Erfasste Menge"].sum()
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_value,
            delta={"reference": faktura_target},
            title={"text": "Wertschöpfende Stunden"},
            gauge={"axis": {"range": [0, faktura_target]}, "bar": {"color": "#636EFA"}},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    gauge_fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        margin=GAUGE_MARGINS,
    )
    config = {"staticPlot": True}
    return gauge_fig, config
