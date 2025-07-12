from typing import Tuple, Dict, Any

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from common.constants import HOURS_PER_PT, DEFAULT_PIE_HEIGHT


def create_faktura_wertschoepfend_pie_chart(
    df_faktura: pd.DataFrame, df_wertschoepfend: pd.DataFrame, df_all: pd.DataFrame
) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Erzeugt einen Pie-Chart, der das Verhältnis von Faktura, Wertschöpfend (aber nicht Faktura)
    und Non-Faktura Projekten in Prozent anzeigt.
    """
    # Berechne die Summe der Stunden für jede Kategorie
    faktura_sum = df_faktura["Erfasste Menge"].sum()
    wertschoepfend_sum = df_wertschoepfend["Erfasste Menge"].sum()
    all_sum = df_all["Erfasste Menge"].sum()

    # Berechne Wertschöpfend (aber nicht Faktura)
    wertschoepfend_not_faktura = wertschoepfend_sum - faktura_sum

    # Berechne Non-Faktura
    non_faktura = all_sum - wertschoepfend_sum

    # Erstelle ein DataFrame für das Pie-Chart
    data = {
        "Kategorie": ["Faktura", "Wertschöpfend (nicht Faktura)", "Non-Faktura"],
        "Stunden": [
            faktura_sum * HOURS_PER_PT,
            wertschoepfend_not_faktura * HOURS_PER_PT,
            non_faktura * HOURS_PER_PT,
        ],
        "PT": [faktura_sum, wertschoepfend_not_faktura, non_faktura],
    }
    df_pie = pd.DataFrame(data)

    # Erstelle das Pie-Chart
    pie_fig = px.pie(
        df_pie,
        names="Kategorie",
        values="Stunden",
        title="Verhältnis Faktura / Wertschöpfend / Non-Faktura",
        labels={"Kategorie": ""},
        custom_data=["PT"],
        template=None,
    )

    # Layout anpassen
    pie_fig.update_layout(
        height=DEFAULT_PIE_HEIGHT, paper_bgcolor="rgba(255,255,255,0)"
    )

    # Prozent-Labels auf dem Chart, Hover mit PT und h
    pie_fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "%{customdata[0]:.2f} PT<br>"
            "%{value:.2f} h<br>"
            "%{percent}"
        ),
    )

    config = {"displaylogo": False}
    return pie_fig, config
