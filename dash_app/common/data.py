import pandas as pd
import datetime
import holidays
import re

_LEISTUNG_STUNDE_RX = re.compile(r"\bStunde\b", flags=re.I)
_LEISTUNG_NON_FAKT_RX = re.compile(r"nicht\s*fakturierte\s*stunde", flags=re.I)


def preprocess_leistung(df: pd.DataFrame) -> pd.DataFrame:
    """
    * verschiebt „Nichtfakturierte Stunde“-Buchungen, die aber auf ein
      Faktura-Projekt (K…, X…) gehen, in ein eigenes Projekt
      (Suffix „ - non Faktura“).
    * liefert eine Kopie des DataFrames zurück, verändert also nichts in-place.
    """
    df = df.copy()

    # ----------------------------------------------------------
    #  1) Non-Faktura-Stunden auf Faktura-Projekten umetikettieren
    # ----------------------------------------------------------
    mask_non_fakt_on_fakt_proj = (
            df["Auftrag/Projekt/Kst."].notna()
            & df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))
            & df["Leistung"].str.contains(_LEISTUNG_NON_FAKT_RX, na=False)
    )
    df.loc[mask_non_fakt_on_fakt_proj, "Auftrag/Projekt/Kst."] = (
            df.loc[mask_non_fakt_on_fakt_proj, "Auftrag/Projekt/Kst."] + " - non Faktura"
    )

    df.loc[mask_non_fakt_on_fakt_proj, "Kurztext"] = (
            df.loc[mask_non_fakt_on_fakt_proj, "Kurztext"] + " - non Faktura"
    )

    return df


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


def get_faktura_projects(df):
    """
    Filtert das DataFrame auf Faktura-Projekte:
    Nur Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist und mit "K" oder "X" beginnt.
    Zudem wird bei "Stunden - CONET Solutions GmbH" der Kurztext anhand der Spalte
    'Positionsbezeichnung' aufgeteilt.
    """
    mask_code = df["Auftrag/Projekt/Kst."].notna() & df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))

    mask_stunde = (
            df["Leistung"].str.contains(_LEISTUNG_STUNDE_RX, na=False)
            & ~df["Leistung"].str.contains(_LEISTUNG_NON_FAKT_RX, na=False)
    )

    df_faktura = df[mask_code & mask_stunde].copy()
    df_faktura = split_allgemein(df_faktura)
    return df_faktura[
        ["ProTime-Datum", "Erfasste Menge", "Auftrag/Projekt/Kst.", "Kurztext"]
    ]


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
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], unit="ms")
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date))
        & (df["ProTime-Datum"] <= pd.to_datetime(end_date))
        ]
    df_grouped = df_filtered.groupby(
        ["Auftrag/Projekt/Kst.", "Kurztext"], as_index=False
    )["Erfasste Menge"].sum()
    df_grouped["Erfasste Menge"] = df_grouped["Erfasste Menge"] / 8
    return df_grouped


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


def import_data(df):
    df = preprocess_leistung(df)
    df_faktura = get_faktura_projects(df)
    df_all = get_all_projects(df)

    return df_all, df_faktura
