import plotly.express as px
import pandas as pd


def filter_and_aggregate_by_interval_stacked(df, start_date, end_date, interval):
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


def create_interval_bar_chart(df_all, start_date, end_date, interval):
    df_agg = filter_and_aggregate_by_interval_stacked(
        df_all, start_date, end_date, interval
    )

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
        height=400,
        template=None,
    )
    fig.update_layout(barmode="stack", paper_bgcolor="rgba(255,255,255,0)")
    fig.update_traces(texttemplate="%{y:.2f}", textposition="auto")
    return fig
