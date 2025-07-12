from typing import Tuple, Dict, Any, Optional
import datetime

import plotly.graph_objects as go
import pandas as pd

from common import data, utils
from common.constants import (
    INTERVAL_CONVERSION,
    GAUGE_MARGINS,
    DEFAULT_INDICATOR_HEIGHT,
    INDICATOR_MARGINS,
)


def create_gauge_chart(
    df_grouped: pd.DataFrame, faktura_target: float
) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Erzeugt einen Gauge-Chart, der die kumulative Faktura (in PT) anzeigt.
    """
    total_value = df_grouped["Erfasste Menge"].sum()
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_value,
            delta={"reference": faktura_target},
            title={"text": "Faktura Total"},
            gauge={"axis": {"range": [0, faktura_target]}},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    gauge_fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        margin=GAUGE_MARGINS,
    )
    config = utils.standard_chart_config(static_plot=True)
    return gauge_fig, config


def create_daily_average_indicators(
    df_faktura: pd.DataFrame,
    df_all: pd.DataFrame,
    start_date: str,
    end_date: str,
    interval: str,
    faktura_target: float,
    vacation_days_pt: int = 0,
) -> Tuple[go.Figure, Dict[str, Any], go.Figure, Dict[str, Any]]:
    """
    Erzeugt zwei Indikatoren:
      - Ø PT pro Intervall (z.B. pro Tag, Woche oder Monat) (Rest zur Zielvorgabe)
      - Ø Stunden pro Intervall (angenommen 8 Stunden pro PT)
    """
    df_faktura["ProTime-Datum"] = pd.to_datetime(df_faktura["ProTime-Datum"], unit="ms")
    df_all["ProTime-Datum"] = pd.to_datetime(df_all["ProTime-Datum"], unit="ms")
    # Gruppiere die Faktura-Daten innerhalb des Datumsbereichs
    df_grouped = data.filter_data_by_date(df_faktura, start_date, end_date)

    # Filtere die ursprünglichen Faktura-Daten (ohne Gruppierung) zur Ermittlung des letzten Buchungstags
    df_filtered = df_faktura[
        (df_faktura["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df_faktura["ProTime-Datum"] <= pd.to_datetime(end_date))
    ]

    faktura_sum = df_grouped["Erfasste Menge"].sum()
    remaining_pt = faktura_target - faktura_sum
    if remaining_pt < 0:
        remaining_pt = 0

    # Ermittle den letzten gebuchten Arbeitstag anhand der Spalte "ProTime-Datum"
    if not df_filtered.empty:
        letzter_buchungstag = pd.to_datetime(df_faktura["ProTime-Datum"]).max().date()
    else:
        letzter_buchungstag = datetime.date.today()

    # Berechne die Anzahl verfügbarer Arbeitstage ab dem letzten gebuchten Arbeitstag bis zum Enddatum
    end_date_date = pd.to_datetime(end_date).date()

    if end_date_date < letzter_buchungstag:
        remaining_days = 0
    else:
        remaining_days = data.get_available_days(
            df_all, start_date=letzter_buchungstag, end_date=end_date_date, vacation_days_pt=vacation_days_pt
        )

    if remaining_days > 0:
        daily_needed_pt = remaining_pt / remaining_days
    else:
        daily_needed_pt = 0

    # Umrechnung je Intervall (Tag, Woche, Monat)
    factor, label = INTERVAL_CONVERSION.get(interval, (1, "Tag"))
    interval_needed_pt = daily_needed_pt * factor
    interval_needed_hours = (
        daily_needed_pt * utils.HOURS_PER_PT * factor
    )  # 8 Stunden pro PT

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
    utils.apply_transparent_background(fig_pt)
    fig_pt.update_layout(
        height=DEFAULT_INDICATOR_HEIGHT,
        margin=INDICATOR_MARGINS,
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
    utils.apply_transparent_background(fig_hours)
    fig_hours.update_layout(
        height=DEFAULT_INDICATOR_HEIGHT,
        margin=INDICATOR_MARGINS,
    )

    config = utils.standard_chart_config(static_plot=True)
    return fig_pt, config, fig_hours, config
