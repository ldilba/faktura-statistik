import plotly.express as px


def create_project_bar_chart(df_grouped):
    # Stunden berechnen
    df_grouped["hours"] = df_grouped["Erfasste Menge"] * 8

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
        height=400,
        paper_bgcolor="rgba(255,255,255,0)"
    )

    # Texttemplate mit PT und h
    bar_fig.update_traces(
        texttemplate="%{y:.2f} PT<br>%{customdata[0]:.0f} h",
        textposition="auto"
    )

    config = {"displaylogo": False}
    return bar_fig, config