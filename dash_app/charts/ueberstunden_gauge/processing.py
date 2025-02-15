import plotly.graph_objects as go
import pandas as pd
import holidays

from common import data


def calculate_expected_hours(start, end):
    """
    Berechnet die erwarteten Sollstunden zwischen start und end,
    unter Berücksichtigung von Wochenenden, Feiertagen (NRW) und
    speziellen Halbtagen (24.12. und 31.03. -> 4 Stunden statt 8).
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
            # Prüfe auf spezielle Halbtage: 24.12. oder 31.03.
            if (day_date.month == 12 and day_date.day == 24) or (
                day_date.month == 3 and day_date.day == 31
            ):
                total_hours += 4
            else:
                total_hours += 8
    return total_hours


def create_verhaeltnis_chart(df_all, start_date, end_date):
    """
    Erstellt ein Indicator-Chart, das die Über-/Unterstunden anzeigt.

    - Die tatsächlich geleisteten Stunden werden als Summe der Spalte "Erfasste Menge" berechnet.
    - Als Sollstunden gelten 8 Stunden pro Tag im angegebenen Zeitraum.
    - Es werden nur Zeilen berücksichtigt, bei denen "Auftrag/Projekt/Kst." einen Wert hat.
    """
    # Filtere das DataFrame (nur Zeilen mit Projektdaten)
    df_all["ProTime-Datum"] = pd.to_datetime(df_all["ProTime-Datum"], unit="ms")
    df_filtered_projects = data.get_all_projects(df_all)

    # Konvertiere die Datumsangaben in datetime (angenommen, "ProTime-Datum" ist bereits datetime)
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # Bestimme das maximale Buchungsdatum in den Daten
    max_buchungsdatum = df_filtered_projects["ProTime-Datum"].max()

    # Falls das Enddatum über das letzte Buchungsdatum hinausgeht, nehmen wir max_buchungsdatum
    effective_end = (
        min(end, max_buchungsdatum) if pd.notnull(max_buchungsdatum) else end
    )


    # Filtere das DataFrame nach Datum
    df_filtered = df_filtered_projects[
        (df_filtered_projects["ProTime-Datum"] >= start)
        & (df_filtered_projects["ProTime-Datum"] <= effective_end)
    ]

    # Summe der tatsächlich geleisteten Stunden
    actual_hours = df_filtered["Erfasste Menge"].sum()

    expected_hours = calculate_expected_hours(start, effective_end)

    # Differenz (positive Zahl: Überstunden, negative Zahl: Unterstunden)
    diff_hours = actual_hours - expected_hours
    title_text = "Überstunden" if diff_hours >= 0 else "Unterstunden"

    # Erstelle das Indicator-Chart
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=diff_hours,
            title={
                "text": f"{title_text}<br>(Differenz zu Sollstunden)",
                "font": {"size": 18},
            },
            number={"suffix": " h", "font": {"size": 35}},
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(t=75, l=50, r=50, b=50),
    )

    config = {"displaylogo": False}
    return fig, config
