import plotly.express as px


def create_verhaeltnis_pie_chart(df_grouped):
    pie_fig = px.pie(
        df_grouped,
        names="Kurztext",
        values="Erfasste Menge",
        title="Verhältnis gebuchte Stunden",
        labels={"Kurztext": ""},
        template=None,
    )
    pie_fig.update_layout(height=400, paper_bgcolor="rgba(255,255,255,0)")
    config = {"displaylogo": False}
    return pie_fig, config
