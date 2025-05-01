import plotly.express as px


def create_verhaeltnis_pie_chart(df_grouped):
    # 1) Stunden-Spalte hinzufügen
    df_grouped["hours"] = df_grouped["Erfasste Menge"] * 8

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
        height=400,
        paper_bgcolor="rgba(255,255,255,0)"
    )

    # 4) Prozent-Labels auf dem Chart, Hover mit PT und h
    pie_fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "%{value} PT<br>"
            "%{customdata[0]:.2f} h<br>"
            "%{percent}"
        )
    )

    config = {"displaylogo": False}
    return pie_fig, config
