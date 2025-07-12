from typing import Tuple, Dict, Any, Optional

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from common import utils


def filter_and_aggregate_by_interval_stacked(
    df: pd.DataFrame, start_date: str, end_date: str, interval: Optional[str]
) -> pd.DataFrame:
    """
    Filtert das komplette Dataset nach Datum und aggregiert die 'Erfasste Menge'
    je nach gewähltem Intervall (z. B. täglich, wöchentlich oder monatlich) und
    gruppiert zusätzlich nach Projekt (Kurztext).
    """
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], unit="ms")
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df["ProTime-Datum"] <= pd.to_datetime(end_date))
    ]
    if interval is None or interval not in ("D", "W", "ME"):
        interval = "D"
    df_agg = (
        df_filtered.groupby(
            [pd.Grouper(key="ProTime-Datum", freq=interval), "Kurztext"]
        )["Erfasste Menge"]
        .sum()
        .reset_index()
    )
    return df_agg


def create_interval_bar_chart(
    df_all: pd.DataFrame, start_date: str, end_date: str, interval: str
) -> Tuple[go.Figure, Dict[str, Any]]:
    df_agg = filter_and_aggregate_by_interval_stacked(
        df_all, start_date, end_date, interval
    )

    # Berechne PT für Custom Hover
    df_agg["PT"] = df_agg["Erfasste Menge"] / 8

    fig = px.bar(
        df_agg,
        x="ProTime-Datum",
        y="Erfasste Menge",
        color="Kurztext",
        title="Stunden Übersicht",
        labels={
            "ProTime-Datum": "",
            "Erfasste Menge": "Stunden",
            "Kurztext": "Projekt",
        },
        height=utils.DEFAULT_BAR_HEIGHT,
        template=None,
        custom_data=["PT"],
    )
    utils.apply_transparent_background(fig)
    fig.update_layout(barmode="stack")
    fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="auto",
        hovertemplate="<b>%{fullData.name}</b><br>"
        + "Datum: %{x}<br>"
        + "Stunden: %{y:.2f} h<br>"
        + "PT: %{customdata[0]:.2f} PT"
        + "<extra></extra>",
    )

    config = utils.standard_chart_config(displaylogo=False)
    return fig, config
