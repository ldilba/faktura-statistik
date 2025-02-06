import plotly.graph_objects as go
import datetime
import pandas as pd
from dash_app.common import data

YEAR_TARGET_PT = 160.0


def create_gauge_chart(df_grouped):
    """
    Erzeugt einen Gauge-Chart, der die kumulative Faktura (in PT) anzeigt.
    """
    total_value = df_grouped["Erfasste Menge"].sum()
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_value,
            delta={"reference": YEAR_TARGET_PT},
            title={"text": "Faktura Total"},
            gauge={"axis": {"range": [0, YEAR_TARGET_PT]}},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    gauge_fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(t=25, l=50, r=50, b=0),
    )
    config = {"staticPlot": True}
    return gauge_fig, config


def create_daily_average_indicators(df_faktura, df_all, start_date, end_date, interval):
    """
    Erzeugt zwei Indikatoren:
      - Ø PT pro Intervall (z. B. pro Tag, Woche oder Monat) (Rest zur Zielvorgabe)
      - Ø Stunden pro Intervall (angenommen 8 Stunden pro PT)
    """
    # Filtere die Faktura-Daten anhand des Datumsbereichs
    df_grouped = data.filter_data_by_date(df_faktura, start_date, end_date)
    faktura_sum = df_grouped["Erfasste Menge"].sum()
    remaining_pt = YEAR_TARGET_PT - faktura_sum
    if remaining_pt < 0:
        remaining_pt = 0

    # Bestimme die Anzahl verfügbarer Arbeitstage (ab heute bis Enddatum)
    today = datetime.date.today()
    end_date_date = pd.to_datetime(end_date).date()
    if end_date_date < today:
        remaining_days = 0
    else:
        remaining_days = data.get_available_days(
            df_all, start_date=today, end_date=end_date_date
        )

    if remaining_days > 0:
        daily_needed_pt = remaining_pt / remaining_days
    else:
        daily_needed_pt = 0

    # Umrechnung je Intervall (Tag, Woche, Monat)
    conversion = {"D": (1, "Tag"), "W": (5, "Woche"), "ME": (22, "Monat")}
    factor, label = conversion.get(interval, (1, "Tag"))
    interval_needed_pt = daily_needed_pt * factor
    interval_needed_hours = daily_needed_pt * 8 * factor  # 8 Stunden pro PT

    # Erzeuge den PT-Indikator
    fig_pt = go.Figure()
    fig_pt.add_trace(
        go.Indicator(
            mode="number",
            value=interval_needed_pt,
            title={"text": f"Ø PT pro {label} (Rest)", "font": {"size": 18}},
            number={"font": {"size": 35}},
        )
    )
    fig_pt.update_layout(
        height=100,
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(t=75, l=50, r=50, b=50),
    )

    # Erzeuge den Stunden-Indikator
    fig_hours = go.Figure()
    fig_hours.add_trace(
        go.Indicator(
            mode="number",
            value=interval_needed_hours,
            title={"text": f"Ø Stunden pro {label} (Rest)", "font": {"size": 18}},
            number={"font": {"size": 35}},
        )
    )
    fig_hours.update_layout(
        height=100,
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(t=75, l=50, r=50, b=50),
    )

    config = {"staticPlot": True}
    return fig_pt, config, fig_hours, config
