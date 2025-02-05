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
        (Urlaub/Krank) sowie Feiertage und Wochenenden berücksichtigt werden.
      - Ein DataFrame (df_bar) mit zusätzlichen Informationen (Datum, Tagestyp,
        Farbe, Opacity, group) zur individuellen Formatierung der Balken im Chart.
    """
    import pandas as pd
    import holidays

    # Konvertiere Datumsangaben in pd.Timestamp
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Erstelle einen täglichen Datumsindex für den gesamten Zeitraum
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # 1. Tatsächliche Faktura berechnen (nur aus df_faktura)
    mask_fact = (df_faktura["ProTime-Datum"] >= start_date) & (
        df_faktura["ProTime-Datum"] <= end_date
    )
    df_fact = df_faktura.loc[mask_fact].copy()
    # Umrechnung: 8 Stunden = 1 PT
    df_fact["Erfasste Menge"] = df_fact["Erfasste Menge"] / 8.0
    # Gruppiere nach Tag und fülle fehlende Tage mit 0
    df_daily = df_fact.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))[
        "Erfasste Menge"
    ].sum()
    df_daily = df_daily.reindex(all_days, fill_value=0)
    actual_cum = df_daily.cumsum()

    # 2. Abwesenheitstage aus df_all ermitteln (getrennt für Urlaub und Krank)
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

    # 3. Feiertage in NRW ermitteln (als Datum-Objekte)
    years = list(range(start_date.year, end_date.year + 1))
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    # 4. Bestimme verfügbare Arbeitstage (wichtig für die Ideallinie)
    available = []
    for day in all_days:
        day_date = day.date()
        # Ein Tag gilt als verfügbar, wenn er ein Werktag (Mo–Fr) ist und
        # nicht als Feiertag, Urlaub oder Krank markiert ist.
        if (
            (day.weekday() < 5)
            and (day_date not in holiday_dates)
            and (day_date not in absent_urlaub)
            and (day_date not in absent_krank)
        ):
            available.append(True)
        else:
            available.append(False)

    # 5. Dynamische Berechnung der Ideallinie (Zielwert wird an verfügbaren Tagen neu verteilt)
    ideal_values = []
    cumulative = 0.0
    remaining_target = float(target)
    for i, day in enumerate(all_days):
        if available[i]:
            remaining_available = sum(
                available[i:]
            )  # noch verfügbare Arbeitstage (inkl. heute)
            daily_increment = (
                remaining_target / remaining_available if remaining_available > 0 else 0
            )
            cumulative += daily_increment
            remaining_target -= daily_increment
        ideal_values.append(cumulative)

    # 6. Erstelle zusätzliche Spalten für den Bar-Plot (Tagestyp, Farbe, Opacity)
    # Bestimme den letzten Tag, an dem tatsächliche Faktura erfasst wurde
    if not df_fact.empty:
        last_fact_date = df_fact["ProTime-Datum"].max().date()
    else:
        last_fact_date = None

    day_types = []
    colors = []
    opacities = []
    groups = (
        []
    )  # Für die Legende: "Wochenende", "Urlaub", "Krankheit", "Feiertag", "Arbeitstag"
    for day in all_days:
        day_date = day.date()
        # Priorität: Feiertag > Urlaub > Krank > Wochenende > normal
        if day_date in holiday_dates:
            d_type = "Feiertag"
            col = "grey"
        elif day_date in absent_urlaub:
            d_type = "Urlaub"
            col = "orange"
        elif day_date in absent_krank:
            d_type = "Krankheit"
            col = "purple"
        elif day.weekday() >= 5:  # Samstag (5) oder Sonntag (6)
            d_type = "Wochenende"
            col = "green"
        else:
            d_type = "normal"
            col = "#1f77b4"  # Standard blau

        # Definiere die Gruppierung: Bei "normal" wird "Arbeitstag" angezeigt.
        grp = "Arbeitstag" if d_type == "normal" else d_type

        opac = 1
        if (
            d_type == "Wochenende"
            or d_type == "Feiertag"
            or d_type == "Urlaub"
            or d_type == "Krankheit"
        ):
            opac = 0.6

        if last_fact_date is not None and day_date > last_fact_date:
            opac = 0.4

        day_types.append(d_type)
        colors.append(col)
        opacities.append(opac)
        groups.append(grp)

    # Erstelle ein DataFrame für die Balken-Informationen
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
    Gibt die Anzahl *verfügbarer* Arbeitstage (Mo–Fr, keine Feiertage in NRW,
    kein Urlaub, keine Krankheit) zurück.
    """
    # Pandas Timestamps
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()

    # Erstelle einen täglichen Datumsindex
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # 1) Urlaub / Krank-Tage herausfinden
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

    # 2) Feiertage (NRW)
    years = range(start_date.year, end_date.year + 1)
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    # 3) Zähle verfügbare Tage
    available_count = 0
    for day in all_days:
        if (
            day.weekday() < 5  # Mo–Fr
            and day not in holiday_dates
            and day not in absent_urlaub
            and day not in absent_krank
        ):
            available_count += 1

    return available_count


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
