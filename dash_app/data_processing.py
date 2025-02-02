import pandas as pd
import datetime
import os

def load_and_clean_data(file_path="data/export20250202202626.xlsx"):
    """Lädt die Excel-Datei und bereinigt die relevanten Daten."""

    print(os.getcwd())  # Zeigt, von welchem Verzeichnis das Skript gestartet wurde

    df = pd.read_excel(file_path)

    # 'ProTime-Datum' als Datum umwandeln
    df['ProTime-Datum'] = pd.to_datetime(df['ProTime-Datum'], errors='coerce')

    # Nur relevante Zeilen behalten
    df_faktura = df[df['Auftrag/Projekt/Kst.'].notna() & df['Auftrag/Projekt/Kst.'].str.startswith(('K', 'X'))][
        ['ProTime-Datum', 'Erfasste Menge', 'Auftrag/Projekt/Kst.', 'Positionsbezeichnung']]

    return df_faktura


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
    """Filtert die Daten nach einem bestimmten Zeitraum."""
    df_filtered = df[(df['ProTime-Datum'] >= pd.to_datetime(start_date)) &
                     (df['ProTime-Datum'] <= pd.to_datetime(end_date))]

    df_grouped = df_filtered.groupby(['Auftrag/Projekt/Kst.', 'Positionsbezeichnung'], as_index=False)[
        'Erfasste Menge'].sum()

    # Umwandlung in PT
    df_grouped['Erfasste Menge'] = df_grouped['Erfasste Menge'] / 8

    return df_grouped
