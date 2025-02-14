import plotly.express as px
from common import data


def create_interval_bar_chart(df_all, start_date, end_date, interval):
    df_agg = data.filter_and_aggregate_by_interval_stacked(
        df_all, start_date, end_date, interval
    )
    print(df_agg)
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
        template="plotly_white",
    )
    fig.update_layout(barmode="stack", paper_bgcolor="rgba(255,255,255,0)")
    fig.update_traces(texttemplate="%{y:.2f}", textposition="auto")
    return fig
