from typing import Tuple, Dict, Any

import plotly.graph_objects as go
import pandas as pd
import holidays

from common import data
from common.constants import HOURS_PER_PT, INDICATOR_MARGINS


def calculate_expected_hours(start: pd.Timestamp, end: pd.Timestamp) -> int:
    """
    Berechnet die erwarteten Sollstunden zwischen start und end,
    unter Berücksichtigung von Wochenenden, Feiertagen (NRW) und
    speziellen Halbtagen (24.12. und 31.12. -> 4 Stunden statt 8).
    """
    # Alle Tage im Zeitraum generieren
    all_days = pd.date_range(start, end, freq="D")

    # Feiertage in NRW bestimmen
    years = list(range(start.year, end.year + 1))
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    total_hours = 0
    for day in all_days:
        day_date = day.date()
        # Nur Wochentage, die keine Feiertage sind
        if day.weekday() < 5 and day_date not in holiday_dates:
            # Prüfe auf spezielle Halbtage: 24.12. oder 31.12.
            if (day_date.month == 12 and day_date.day == 24) or (
                day_date.month == 12 and day_date.day == 31
            ):
                total_hours += 4
            else:
                total_hours += HOURS_PER_PT
    return total_hours


def create_faktura_ueberstunden_chart(
    df_all: pd.DataFrame, start_date: str, end_date: str
) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Erstellt ein Indicator-Chart, das die Faktura-Überstunden anzeigt.

    - Faktura-Überstunden können nur positiv sein.
    - Faktura-Überstunden werden nur berechnet, wenn an einem Tag mehr als 8 Stunden
      Faktura-Arbeit geleistet wurden.
    - Jede Faktura-Stunde über 8 Stunden pro Tag zählt als Faktura-Überstunde.
    - Minderstunden (weniger als 8 Stunden pro Tag) werden von den Überstunden abgezogen,
      bis maximal 0.
    """
    # Filtere das DataFrame (nur Zeilen mit Faktura-Projektdaten)
    df_all["ProTime-Datum"] = pd.to_datetime(df_all["ProTime-Datum"], unit="ms")
    df_faktura = data.get_faktura_projects(df_all)

    # Konvertiere die Datumsangaben in datetime
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # Bestimme das maximale Buchungsdatum in den Daten
    max_buchungsdatum = df_faktura["ProTime-Datum"].max()

    # Falls das Enddatum über das letzte Buchungsdatum hinausgeht, nehmen wir max_buchungsdatum
    effective_end = (
        min(end, max_buchungsdatum) if pd.notnull(max_buchungsdatum) else end
    )

    # Filtere das DataFrame nach Datum
    df_filtered = df_faktura[
        (df_faktura["ProTime-Datum"] >= start)
        & (df_faktura["ProTime-Datum"] <= effective_end)
    ]

    # Gruppiere nach Datum und summiere die Stunden pro Tag
    df_daily = (
        df_filtered.groupby(df_filtered["ProTime-Datum"].dt.date)["Erfasste Menge"]
        .sum()
        .reset_index()
    )

    # Berechne die Faktura-Überstunden pro Tag (Stunden über 8 pro Tag)
    df_daily["Faktura_Ueberstunden"] = df_daily["Erfasste Menge"].apply(
        lambda x: max(0, x - HOURS_PER_PT)
    )

    # Berechne die Minderstunden pro Tag (Stunden unter 8 pro Tag)
    df_daily["Minderstunden"] = df_daily["Erfasste Menge"].apply(
        lambda x: min(0, x - HOURS_PER_PT)
    )

    # Summe der Faktura-Überstunden und Minderstunden
    faktura_ueberstunden = df_daily["Faktura_Ueberstunden"].sum()
    minderstunden = abs(df_daily["Minderstunden"].sum())

    # Ziehe Minderstunden von Überstunden ab, aber nicht unter 0
    faktura_ueberstunden = max(0, faktura_ueberstunden - minderstunden)

    # Faktura-Überstunden sind immer positiv
    title_text = "Faktura-Überstunden"

    # Erstelle das Indicator-Chart
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=faktura_ueberstunden,
            title={
                "text": f"{title_text}<br>(Stunden über 8h/Tag<br>minus Minderstunden)",
                "font": {"size": 18},
            },
            number={"suffix": " h", "font": {"size": 35}},
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        margin=INDICATOR_MARGINS,
    )

    config = {"displaylogo": False}
    return fig, config
