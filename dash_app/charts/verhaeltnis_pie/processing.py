from typing import Tuple, Dict, Any

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from common.constants import HOURS_PER_PT, DEFAULT_PIE_HEIGHT


def create_verhaeltnis_pie_chart(
    df_grouped: pd.DataFrame,
) -> Tuple[go.Figure, Dict[str, Any]]:
    # 1) Stunden-Spalte hinzufügen
    df_grouped["hours"] = df_grouped["Erfasste Menge"] * HOURS_PER_PT

    # 2) Pie-Chart mit custom_data für hours
    pie_fig = px.pie(
        df_grouped,
        names="Kurztext",
        values="Erfasste Menge",
        title="Verhältnis gebuchte Stunden",
        labels={"Kurztext": ""},
        custom_data=["hours"],
        template=None,
    )

    # 3) Layout anpassen
    pie_fig.update_layout(
        height=DEFAULT_PIE_HEIGHT, paper_bgcolor="rgba(255,255,255,0)"
    )

    # 4) Prozent-Labels auf dem Chart, Hover mit PT und h
    pie_fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>" "%{value} PT<br>" "%{customdata[0]:.2f} h<br>" "%{percent}"
        ),
    )

    config = {"displaylogo": False}
    return pie_fig, config
