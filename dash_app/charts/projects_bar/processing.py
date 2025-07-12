from typing import Tuple, Dict, Any

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from common.constants import HOURS_PER_PT, DEFAULT_BAR_HEIGHT


def create_project_bar_chart(
    df_grouped: pd.DataFrame,
) -> Tuple[go.Figure, Dict[str, Any]]:
    # Stunden berechnen
    df_grouped["hours"] = df_grouped["Erfasste Menge"] * HOURS_PER_PT

    # Bar-Chart, custom_data enthält jetzt die hours-Spalte
    bar_fig = px.bar(
        df_grouped,
        x="Kurztext",
        y="Erfasste Menge",
        title="Tage Faktura nach Projekt",
        labels={"Kurztext": ""},
        custom_data=["hours"],
        template=None,
    )

    bar_fig.update_layout(
        height=DEFAULT_BAR_HEIGHT, paper_bgcolor="rgba(255,255,255,0)"
    )

    # Texttemplate mit PT und h
    bar_fig.update_traces(
        texttemplate="%{y:.2f} PT<br>%{customdata[0]:.0f} h",
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>"
        + "Faktura: %{y:.2f} PT<br>"
        + "Faktura: %{customdata[0]:.0f} h"
        + "<extra></extra>",
    )

    config = {"displaylogo": False}
    return bar_fig, config
