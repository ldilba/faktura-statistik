import pandas as pd
import datetime
import os


def load_and_clean_data(file_path="data/export20250202202626.xlsx"):
    """Lädt die Excel-Datei und filtert auf Faktura-Projekte (Auftrag/Projekt/Kst. beginnt mit 'K' oder 'X')."""
    print(os.getcwd())  # Zeigt, von welchem Verzeichnis das Skript gestartet wurde
    df = pd.read_excel(file_path)
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], errors="coerce")

    # Nur Faktura-Projekte: Zeilen behalten, bei denen die Spalte "Auftrag/Projekt/Kst." mit "K" oder "X" beginnt
    df_faktura = df[
        df["Auftrag/Projekt/Kst."].notna() &
        df["Auftrag/Projekt/Kst."].str.startswith(("K", "X"))
        ][["ProTime-Datum", "Erfasste Menge", "Auftrag/Projekt/Kst.", "Kurztext"]]

    return df_faktura


def load_all_data(file_path="data/export20250202202626.xlsx"):
    """Lädt die Excel-Datei und bereitet sie auf – ohne die Filterung auf Faktura-Projekte."""
    df = pd.read_excel(file_path)
    df["ProTime-Datum"] = pd.to_datetime(df["ProTime-Datum"], errors="coerce")
    return df


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
    Filtert die Daten nach Datum und gruppiert (hier für das Gauge/Balkendiagramm,
    welches nur Faktura-Projekte verwenden soll).
    """
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date)) &
        (df["ProTime-Datum"] <= pd.to_datetime(end_date))
        ]
    # Gruppierung nach Projekt (Auftrag/Projekt/Kst. und Kurztext) und Summe der Erfassten Menge
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
    # Daten nach Datum filtern
    df_filtered = df[
        (df["ProTime-Datum"] >= pd.to_datetime(start_date)) &
        (df["ProTime-Datum"] <= pd.to_datetime(end_date))
        ]

    # Frequenz festlegen
    if interval == "Tag":
        freq = "D"
    elif interval == "Woche":
        freq = "W"
    elif interval == "Monat":
        freq = "M"
    else:
        freq = "D"  # Fallback

    # Gruppierung nach Datum (entsprechend der Frequenz) und nach Projekt (Kurztext)
    df_agg = df_filtered.groupby(
        [pd.Grouper(key="ProTime-Datum", freq=freq), "Kurztext"]
    )["Erfasste Menge"].sum().reset_index()

    return df_agg


# Globale Datenbasis:
# df_full enthält nur Faktura-Projekte (für die anderen Diagramme)
df_full = load_and_clean_data()

# df_all enthält alle Projekte (für das gestackte Intervall-Bar-Chart)
df_all = load_all_data()
