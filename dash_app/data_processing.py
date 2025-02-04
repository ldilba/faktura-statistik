import pandas as pd
import datetime
import os


def split_allgemein(df):
    """
    Sucht in der Spalte 'Kurztext' nach dem Wert "Stunden - CONET Solutions GmbH".
    Für diese Zeilen wird der 'Kurztext' durch den Inhalt der Spalte
    'Positionsbezeichnung' ersetzt. Falls dort mehrere Projekte (z. B. kommasepariert)
    stehen, wird in mehrere Zeilen aufgeteilt.
    """
    mask = df["Kurztext"] == "Stunden - CONET Solutions GmbH"
    if "Positionsbezeichnung" in df.columns:
        # Ersetze den 'Kurztext' mit einer Liste der Projekte, falls mehrere Projekte durch Komma getrennt sind
        df.loc[mask, "Kurztext"] = df.loc[mask, "Positionsbezeichnung"].apply(
            lambda x: (
                [proj.strip() for proj in x.split(",")] if isinstance(x, str) else x
            )
        )
        # Explodiere die Zeilen, sodass für jeden Eintrag ein eigener Datensatz entsteht
        df = df.explode("Kurztext")
    return df


def load_and_clean_data(file_path="data/export20250202202626.xlsx"):
    """
    Lädt die Excel-Datei und filtert auf Faktura-Projekte:
    Nur Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist und mit "K" oder "X" startet.
    Außerdem wird für den Fall, dass in 'Kurztext' der Wert
    "Stunden - CONET Solutions GmbH" steht, die Aufteilung anhand von 'Positionsbezeichnung' vorgenommen.
    """
    print(os.getcwd())  # Zeigt, von welchem Verzeichnis das Skript gestartet wurde
    df = pd.read_excel(file_path)
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], errors="coerce")

    # Filtere zunächst Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist und mit "K" oder "X" beginnt
    df_faktura = df[
        df["Auftrag/Projekt/Kst."].notna()
        & df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))
    ]

    # Wende den Split für "Stunden - CONET Solutions GmbH" an
    df_faktura = split_allgemein(df_faktura)

    # Spaltenauswahl (ggf. anpassen, falls weitere Spalten benötigt werden)
    df_faktura = df_faktura[
        ["ProTime-Datum", "Erfasste Menge", "Auftrag/Projekt/Kst.", "Kurztext"]
    ]
    return df_faktura


def load_all_data(file_path="data/export20250202202626.xlsx"):
    """
    Lädt die Excel-Datei und behält alle Zeilen, in denen "Auftrag/Projekt/Kst." nicht NA ist.
    Auch hier wird der Split für 'Stunden - CONET Solutions GmbH' vorgenommen,
    sodass in 'Kurztext' für diese Zeilen die Projekte aus 'Positionsbezeichnung' stehen.
    """
    df = pd.read_excel(file_path)
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], errors="coerce")
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
    Hier wird davon ausgegangen, dass das DataFrame bereits den erforderlichen Filter
    (Faktura-Projekte) enthält.
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

    print(interval)
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


# Globale Datenbasis:
# df_full: nur Faktura-Projekte (wobei 'Stunden - CONET Solutions GmbH' aufgeteilt wurde)
df_full = load_and_clean_data()

# df_all: alle Projekte (ebenfalls mit Aufteilung, wenn 'Stunden - CONET Solutions GmbH' vorkommt)
df_all = load_all_data()
