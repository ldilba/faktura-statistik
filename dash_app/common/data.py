import os

import pandas as pd
import datetime
import holidays


# from dash_app.app import app


def split_allgemein(df):
    """
    Sucht in der Spalte 'Kurztext' nach dem Wert "Stunden - CONET Solutions GmbH".
    Für diese Zeilen wird der 'Kurztext' durch den Inhalt der Spalte
    'Positionsbezeichnung' ersetzt. Falls mehrere Projekte (z. B. kommasepariert)
    vorhanden sind, wird in mehrere Zeilen aufgeteilt.
    """
    mask = df["Kurztext"] == "Stunden - CONET Solutions GmbH"
    if "Positionsbezeichnung" in df.columns:
        df.loc[mask, "Kurztext"] = df.loc[mask, "Positionsbezeichnung"].apply(
            lambda x: (
                [proj.strip() for proj in x.split(",")] if isinstance(x, str) else x
            )
        )
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
    Zudem wird bei "Stunden - CONET Solutions GmbH" der Kurztext anhand der Spalte
    'Positionsbezeichnung' aufgeteilt.
    """
    df_faktura = df[
        df["Auftrag/Projekt/Kst."].notna()
        & df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))
    ]
    df_faktura = split_allgemein(df_faktura)
    df_faktura = df_faktura[
        ["ProTime-Datum", "Erfasste Menge", "Auftrag/Projekt/Kst.", "Kurztext"]
    ]
    return df_faktura


def get_all_projects(df):
    """
    Filtert das DataFrame auf alle Projekte (nur Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist)
    und wendet ebenfalls die Aufteilung für "Stunden - CONET Solutions GmbH" an.
    """
    df_all = df[df["Auftrag/Projekt/Kst."].notna()]
    df_all = split_allgemein(df_all)
    return df_all


def get_fiscal_year_range():
    """
    Bestimmt den aktuellen Geschäftsjahresbereich (1. April bis 31. März).
    """
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
    Filtert das DataFrame nach Datum (basierend auf 'ProTime-Datum') und gruppiert
    nach ["Auftrag/Projekt/Kst.", "Kurztext"]. Dabei wird die 'Erfasste Menge'
    in PT (8 Stunden = 1 PT) umgerechnet.
    """
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df["ProTime-Datum"] <= pd.to_datetime(end_date))
    ]
    df_grouped = df_filtered.groupby(
        ["Auftrag/Projekt/Kst.", "Kurztext"], as_index=False
    )["Erfasste Menge"].sum()
    df_grouped["Erfasste Menge"] = df_grouped["Erfasste Menge"] / 8
    return df_grouped


def filter_and_aggregate_by_interval_stacked(df, start_date, end_date, interval):
    """
    Filtert das komplette Dataset nach Datum und aggregiert die 'Erfasste Menge'
    je nach gewähltem Intervall (z. B. täglich, wöchentlich oder monatlich) und
    gruppiert zusätzlich nach Projekt (Kurztext).
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
      - Eine dynamisch berechnete Ideallinie (in PT), unter Berücksichtigung von
        Feiertagen, Urlaub, Krankheit und Wochenenden.
      - Ein DataFrame (df_bar) mit zusätzlichen Informationen (Datum, Tagestyp,
        Farbe, Opacity, Gruppe) zur individuellen Formatierung der Balken im Chart.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Tatsächliche Faktura berechnen (8 Stunden = 1 PT)
    mask_fact = (df_faktura["ProTime-Datum"] >= start_date) & (
        df_faktura["ProTime-Datum"] <= end_date
    )
    df_fact = df_faktura.loc[mask_fact].copy()
    df_fact["Erfasste Menge"] = df_fact["Erfasste Menge"] / 8.0
    df_daily = df_fact.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))[
        "Erfasste Menge"
    ].sum()
    df_daily = df_daily.reindex(all_days, fill_value=0)
    actual_cum = df_daily.cumsum()

    # Abwesenheitstage (Urlaub und Krankheit)
    absent_urlaub = set()
    absent_krank = set()
    if "Positionsbezeichnung" in df_all.columns:
        vacation_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Urlaub")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_urlaub = set(vacation_rows["ProTime-Datum"].dt.normalize().dt.date)
        krank_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Krank")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_krank = set(krank_rows["ProTime-Datum"].dt.normalize().dt.date)

    # Feiertage in NRW bestimmen
    years = list(range(start_date.year, end_date.year + 1))
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    # Verfügbare Arbeitstage bestimmen
    available = []
    for day in all_days:
        day_date = day.date()
        if (
            (day.weekday() < 5)
            and (day_date not in holiday_dates)
            and (day_date not in absent_urlaub)
            and (day_date not in absent_krank)
        ):
            available.append(True)
        else:
            available.append(False)

    # Dynamische Ideallinie berechnen
    ideal_values = []
    cumulative = 0.0
    remaining_target = float(target)
    for i, day in enumerate(all_days):
        if available[i]:
            remaining_available = sum(available[i:])
            daily_increment = (
                remaining_target / remaining_available if remaining_available > 0 else 0
            )
            cumulative += daily_increment
            remaining_target -= daily_increment
        ideal_values.append(cumulative)

    # Zusätzliche Daten für den Bar-Plot (z. B. zur individuellen Formatierung)
    if not df_fact.empty:
        last_fact_date = df_fact["ProTime-Datum"].max().date()
    else:
        last_fact_date = None

    # Für jeden Tag werden Tagestyp, Farbe, Opacity und Gruppe bestimmt:
    day_types = []
    colors = []
    opacities = []
    groups = []
    for day in all_days:
        day_date = day.date()
        if day_date in holiday_dates:
            d_type = "Feiertag"
            col = "grey"
        elif day_date in absent_urlaub:
            d_type = "Urlaub"
            col = "orange"
        elif day_date in absent_krank:
            d_type = "Krankheit"
            col = "purple"
        elif day.weekday() >= 5:
            d_type = "Wochenende"
            col = "green"
        else:
            d_type = "normal"
            col = "#1f77b4"
        grp = "Arbeitstag" if d_type == "normal" else d_type
        opac = 1
        if d_type in ["Wochenende", "Feiertag", "Urlaub", "Krankheit"]:
            opac = 0.6
        if last_fact_date is not None and day_date > last_fact_date:
            opac = 0.4
        day_types.append(d_type)
        colors.append(col)
        opacities.append(opac)
        groups.append(grp)

    df_bar = pd.DataFrame(
        {
            "Datum": all_days,
            "Tatsächliche Faktura": actual_cum.values,
            "day_type": day_types,
            "color": colors,
            "opacity": opacities,
            "group": groups,
        }
    )

    return all_days, actual_cum, ideal_values, df_bar


def get_available_days(df_all, start_date, end_date):
    """
    Gibt die Anzahl der verfügbaren Arbeitstage (Mo–Fr, ohne Feiertage, Urlaub und Krankheit)
    im angegebenen Zeitraum zurück.
    """
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    absent_urlaub = set()
    absent_krank = set()
    if "Positionsbezeichnung" in df_all.columns:
        vacation_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Urlaub")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_urlaub = set(vacation_rows["ProTime-Datum"].dt.normalize())
        krank_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Krank")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_krank = set(krank_rows["ProTime-Datum"].dt.normalize())

    years = range(start_date.year, end_date.year + 1)
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    available_count = 0
    for day in all_days:
        if (
            (day.weekday() < 5)
            and (day not in holiday_dates)
            and (day not in absent_urlaub)
            and (day not in absent_krank)
        ):
            available_count += 1
    return available_count


df_raw = pd.DataFrame()
df_faktura = pd.DataFrame()
df_all = pd.DataFrame()

fiscal_start = datetime.date.today()
fiscal_end = datetime.date.today()
df_grouped = pd.DataFrame()

df_aggregated = pd.DataFrame()


def import_data(file):
    global df_raw
    global df_faktura
    global df_all
    global fiscal_start
    global fiscal_end
    global df_grouped
    global df_aggregated
    df_raw = load_data(file)
    df_faktura = get_faktura_projects(df_raw)
    df_all = get_all_projects(df_raw)

    fiscal_start, fiscal_end = get_fiscal_year_range()
    df_grouped = filter_data_by_date(df_faktura, fiscal_start, fiscal_end)
    df_aggregated = filter_and_aggregate_by_interval_stacked(
        df_all, fiscal_start, fiscal_end, interval="D"
    )


def find_excel_file(directory="data"):
    # Stelle sicher, dass das Verzeichnis existiert
    if not os.path.exists(directory):
        return None

    # Durchsucht das Verzeichnis nach .xlsx-Dateien
    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            return os.path.join(directory, file)  # Gibt den vollständigen Pfad zurück

    return None  # Falls keine Datei gefunden wurde


def first_import(app):
    excel_file = find_excel_file()
    if excel_file:
        import_data(file=f"{excel_file}")
        app.server.config["data_loaded"] = True
        app.server.config["update_trigger"] = {"update": True}
