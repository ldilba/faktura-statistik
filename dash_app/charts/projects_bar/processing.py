import plotly.express as px


def create_project_bar_chart(df_grouped):
    bar_fig = px.bar(
        df_grouped,
        x="Kurztext",
        y="Erfasste Menge",
        title="Tage Faktura nach Projekt",
        labels={"Kurztext": ""},
        template=None,
    )
    bar_fig.update_layout(height=400, paper_bgcolor="rgba(255,255,255,0)")
    bar_fig.update_traces(texttemplate="%{y:.2f} PT", textposition="auto")
    config = {"displaylogo": False}
    return bar_fig, config
