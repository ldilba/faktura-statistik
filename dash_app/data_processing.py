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


def get_burndown_data(df_faktura, df_all, start_date, end_date, target=160):
    """
    Berechnet:
      - Die kumulative tatsächliche Faktura (in PT) basierend auf df_faktura.
      - Die dynamisch berechnete Ideallinie (in PT), wobei Abwesenheitstage
        (Urlaub/Krank, ermittelt aus df_all) sowie Feiertage und Wochenenden berücksichtigt werden.

    Parameter:
      df_faktura: DataFrame mit Faktura-Daten (z. B. wie in get_faktura_projects),
                  aus denen die tatsächlich geleistete Faktura berechnet wird.
      df_all: DataFrame mit allen Projekten (enthält u.a. "Positionsbezeichnung"),
              um Abwesenheitstage (Urlaub/Krank) zu erkennen.
      start_date, end_date: Zeitraum (string oder pd.Timestamp).
      target: Zielwert in PT (Standard: 160).

    Returns:
      all_days: pd.DatetimeIndex aller Tage im Zeitraum.
      actual_cum: Series mit der kumulierten tatsächlichen Faktura (in PT) pro Tag.
      ideal_values: Liste mit den dynamisch berechneten kumulativen Idealwerten (in PT).
    """

    # Konvertiere die Datumsangaben in pd.Timestamp
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Erstelle den täglichen Datumsindex für den gesamten Zeitraum
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # 1. Tatsächliche Faktura (nur aus df_faktura, damit keine unerwünschten Einträge dabei sind)
    mask_fact = (df_faktura["ProTime-Datum"] >= start_date) & (
        df_faktura["ProTime-Datum"] <= end_date
    )
    df_fact = df_faktura.loc[mask_fact].copy()
    # Umrechnung in PT (8 Stunden = 1 PT)
    df_fact["Erfasste Menge"] = df_fact["Erfasste Menge"] / 8.0
    # Gruppieren nach Tag
    df_daily = df_fact.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))[
        "Erfasste Menge"
    ].sum()
    df_daily = df_daily.reindex(all_days, fill_value=0)
    actual_cum = df_daily.cumsum()

    # 2. Ideallinie berechnen (mit Abwesenheitsdaten aus df_all)
    # Ermitteln der Abwesenheitstage (Urlaub/Krank) aus df_all
    absent_dates = set()
    if "Positionsbezeichnung" in df_all.columns:
        absent_rows = df_all.loc[
            (df_all["Positionsbezeichnung"].isin(["Urlaub", "Krank"]))
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_dates = set(absent_rows["ProTime-Datum"].dt.normalize().dt.date)

    # Feiertage in NRW
    years = list(range(start_date.year, end_date.year + 1))
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    # Bestimme verfügbare Arbeitstage: Arbeitstag, wenn
    # - Wochentag (Mo-Fr)
    # - kein Feiertag in NRW
    # - nicht als Urlaub/Krank markiert
    available = []
    for day in all_days:
        day_date = day.date()
        if (
            (day.weekday() < 5)
            and (day_date not in holiday_dates)
            and (day_date not in absent_dates)
        ):
            available.append(True)
        else:
            available.append(False)

    # Dynamische Berechnung der Ideallinie:
    ideal_values = []
    cumulative = 0.0
    remaining_target = float(target)
    # Für jeden Tag: Wenn verfügbar, wird der noch zu leistende Wert anteilig aufgeteilt.
    for i, day in enumerate(all_days):
        if available[i]:
            remaining_available = sum(
                available[i:]
            )  # Anzahl der noch verfügbaren Arbeitstage (inkl. heute)
            if remaining_available > 0:
                daily_increment = remaining_target / remaining_available
            else:
                daily_increment = 0
            cumulative += daily_increment
            remaining_target -= daily_increment
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
