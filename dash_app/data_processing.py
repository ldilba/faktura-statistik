import pandas as pd
import datetime
import holidays


def split_allgemein(df):
    """
    Sucht in der Spalte 'Kurztext' nach dem Wert "Stunden - CONET Solutions GmbH".
    Für diese Zeilen wird der 'Kurztext' durch den Inhalt der Spalte
    'Positionsbezeichnung' ersetzt. Falls dort mehrere Projekte (z. B. kommasepariert)
    stehen, wird in mehrere Zeilen aufgeteilt.
    """
    mask = df["Kurztext"] == "Stunden - CONET Solutions GmbH"
    if "Positionsbezeichnung" in df.columns:
        # Ersetze den 'Kurztext' durch eine Liste der Projekte, falls mehrere kommasepariert vorhanden sind
        df.loc[mask, "Kurztext"] = df.loc[mask, "Positionsbezeichnung"].apply(
            lambda x: (
                [proj.strip() for proj in x.split(",")] if isinstance(x, str) else x
            )
        )
        # Explodiere die Zeilen, sodass für jeden Eintrag ein eigener Datensatz entsteht
        df = df.explode("Kurztext")
    return df


def load_data(file_path):
    """
    Lädt die Excel-Datei und konvertiert die Datumsspalte.
    """
    df = pd.read_excel(file_path)
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], errors="coerce")
    return df


def get_faktura_projects(df):
    """
    Filtert das DataFrame auf Faktura-Projekte:
    Nur Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist und mit "K" oder "X" beginnt.
    Zudem wird für den Fall, dass in 'Kurztext' der Wert "Stunden - CONET Solutions GmbH" vorkommt,
    die Aufteilung anhand von 'Positionsbezeichnung' vorgenommen.
    """
    df_faktura = df[
        df["Auftrag/Projekt/Kst."].notna()
        & df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))
    ]
    df_faktura = split_allgemein(df_faktura)
    # Spaltenauswahl (ggf. anpassen, falls weitere Spalten benötigt werden)
    df_faktura = df_faktura[
        ["ProTime-Datum", "Erfasste Menge", "Auftrag/Projekt/Kst.", "Kurztext"]
    ]
    return df_faktura


def get_all_projects(df):
    """
    Filtert das DataFrame auf alle Projekte (nur Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist)
    und wendet ebenfalls die Aufteilung für 'Stunden - CONET Solutions GmbH' an.
    """
    df_all = df[df["Auftrag/Projekt/Kst."].notna()]
    df_all = split_allgemein(df_all)
    return df_all


def get_fiscal_year_range():
    """Bestimmt den aktuellen Geschäftsjahresbereich (1. April bis 31. März)."""
    today = datetime.date.today()
    current_year = today.year
    if today.month < 4:
        fiscal_start = datetime.date(current_year - 1, 4, 1)
        fiscal_end = datetime.date(current_year, 3, 31)
    else:
        fiscal_start = datetime.date(current_year, 4, 1)
        fiscal_end = datetime.date(current_year + 1, 3, 31)
    return fiscal_start, fiscal_end


def filter_data_by_date(df, start_date, end_date):
    """
    Filtert die Daten nach einem bestimmten Zeitraum und gruppiert nach
    ["Auftrag/Projekt/Kst.", "Kurztext"].
    Hier wird davon ausgegangen, dass das DataFrame bereits den erforderlichen Filter (Faktura-Projekte) enthält.
    """
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df["ProTime-Datum"] <= pd.to_datetime(end_date))
    ]
    df_grouped = df_filtered.groupby(
        ["Auftrag/Projekt/Kst.", "Kurztext"], as_index=False
    )["Erfasste Menge"].sum()
    # Umrechnung in PT (angenommen, 8 Stunden = 1 PT)
    df_grouped["Erfasste Menge"] = df_grouped["Erfasste Menge"] / 8
    return df_grouped


def filter_and_aggregate_by_interval_stacked(df, start_date, end_date, interval):
    """
    Filtert das (komplette) Dataset nach Datum und aggregiert die 'Erfasste Menge'
    je nach gewähltem Intervall (Tag, Woche, Monat) und gruppiert zusätzlich nach Projekt (Kurztext).
    """
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df["ProTime-Datum"] <= pd.to_datetime(end_date))
    ]

    if interval is None or interval not in ("D", "W", "ME"):
        interval = "D"

    df_agg = (
        df_filtered.groupby(
            [pd.Grouper(key="ProTime-Datum", freq=interval), "Kurztext"]
        )["Erfasste Menge"]
        .sum()
        .reset_index()
    )
    return df_agg

def get_burndown_data(df, start_date, end_date, target=160):
    """
    Berechnet für den gegebenen DataFrame die kumulative tatsächliche Faktura (in PT)
    und die Ideallinie für ein (invertiertes) Burndown Chart.

    Dabei wird:
      - Der DataFrame nach dem Zeitraum [start_date, end_date] gefiltert.
      - Die "Erfasste Menge" in PT umgerechnet (8 Stunden = 1 PT).
      - Pro Tag die Faktura summiert und kumulativ aufsummiert.
      - Eine Ideallinie berechnet, die auf Arbeitstagen (Mo-Fr, ohne Feiertage in NRW)
        basiert. An diesen Tagen wird ein täglicher Zuwachs errechnet, sodass
        insgesamt `target` PT erreicht werden.

    Parameter:
      df: DataFrame mit Faktura-Daten. Erwartet werden die Spalten "ProTime-Datum" (Datum)
          und "Erfasste Menge" (Stunden).
      start_date: Startdatum des Zeitraums (string oder pd.Timestamp).
      end_date: Enddatum des Zeitraums (string oder pd.Timestamp).
      target: Zielwert in PT (Standard: 160, entspricht 160 Faktura-Tagen).

    Returns:
      all_days: pd.DatetimeIndex aller Tage im Zeitraum.
      actual_cum: Pandas Series mit der kumulierten tatsächlichen Faktura (in PT) pro Tag.
      ideal_values: Liste mit der kumulativen Ideallinie (in PT) für jeden Tag.
    """
    # Umwandlung der Datumsangaben in pd.Timestamp
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Erstelle einen täglichen Datumsindex für den gesamten Zeitraum
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')

    # Filtere den DataFrame nach Datum
    mask = (df["ProTime-Datum"] >= start_date) & (df["ProTime-Datum"] <= end_date)
    df_filtered = df.loc[mask].copy()

    # Umrechnung in PT (8 Stunden = 1 PT)
    df_filtered["Erfasste Menge"] = df_filtered["Erfasste Menge"] / 8.0

    # Gruppiere die Daten pro Tag und summiere die Faktura
    df_daily = df_filtered.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))["Erfasste Menge"].sum()
    # Alle Tage sicherstellen – fehlende Tage werden mit 0 aufgefüllt
    df_daily = df_daily.reindex(all_days, fill_value=0)
    # Kumulativer Fortschritt der tatsächlichen Faktura
    actual_cum = df_daily.cumsum()

    # Berechnung der Ideallinie:
    # Bestimme alle beteiligten Jahre, um die Feiertage korrekt zu ermitteln.
    years = list(range(start_date.year, end_date.year + 1))
    nrw_holidays = holidays.Germany(prov='NW', years=years)

    # Bestimme alle Arbeitstage (Mo-Fr, die nicht in den NRW-Feiertagen liegen)
    working_days = [day for day in all_days if (day.weekday() < 5 and day.date() not in nrw_holidays)]

    if len(working_days) == 0:
        daily_increment = 0
    else:
        daily_increment = target / len(working_days)

    ideal_values = []
    cumulative = 0
    # Für jeden Tag: Wenn Arbeitstag, füge daily_increment hinzu, sonst bleibt der Wert gleich
    for day in all_days:
        if day.weekday() < 5 and day.date() not in nrw_holidays:
            cumulative += daily_increment
        ideal_values.append(cumulative)

    return all_days, actual_cum, ideal_values

# === Hauptprogramm: Excel nur einmal laden ===

# Excel-Datei einlesen
df_raw = load_data("data/export20250202202626.xlsx")

# Faktura-Projekte (mit der Aufteilung von "Stunden - CONET Solutions GmbH")
df_faktura = get_faktura_projects(df_raw)

# Alle Projekte (ebenfalls mit der Aufteilung)
df_all = get_all_projects(df_raw)

# Beispiel: Daten nach Geschäftsjahr filtern und aggregieren
fiscal_start, fiscal_end = get_fiscal_year_range()
df_grouped = filter_data_by_date(df_faktura, fiscal_start, fiscal_end)

# Beispiel: Daten nach Intervall aggregieren (z.B. täglich "D")
df_aggregated = filter_and_aggregate_by_interval_stacked(
    df_all, fiscal_start, fiscal_end, interval="D"
)
