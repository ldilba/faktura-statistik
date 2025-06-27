import plotly.express as px
import pandas as pd


def create_faktura_wertschoepfend_pie_chart(df_faktura, df_wertschoepfend, df_all):
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
        "Stunden": [faktura_sum * 8, wertschoepfend_not_faktura * 8, non_faktura * 8],
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
    pie_fig.update_layout(height=400, paper_bgcolor="rgba(255,255,255,0)")

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
