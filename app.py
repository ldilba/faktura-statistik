from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# Dash App initialisieren
app = Dash()

# Daten laden
df = pd.read_excel("export20250202202626.xlsx")

# 'ProTime-Datum' als Datum umwandeln
df['ProTime-Datum'] = pd.to_datetime(df['ProTime-Datum'], errors='coerce')

# Nur relevante Daten filtern
dfFaktura = df[df['Auftrag/Projekt/Kst.'].notna() & df['Auftrag/Projekt/Kst.'].str.startswith(('K', 'X'))][
    ['ProTime-Datum', 'Erfasste Menge', 'Auftrag/Projekt/Kst.', 'Positionsbezeichnung']]

# 📅 Aktuelles Datum bestimmen
today = datetime.date.today()
current_year = today.year

# 📅 Geschäftsjahr bestimmen (Start: 1. März Vorjahr, Ende: 1. März Aktuelles Jahr)
if today.month < 4:  # Falls wir im Januar oder Februar sind
    fiscal_start = datetime.date(current_year - 1, 4, 1)
    fiscal_end = datetime.date(current_year, 3, 31)
else:
    fiscal_start = datetime.date(current_year, 4, 1)
    fiscal_end = datetime.date(current_year + 1, 3, 31)

# App-Layout mit DatePicker
app.layout = html.Div([
    html.H1(children='Dash App', style={'textAlign': 'center'}),

    # Datumsauswahl (Start- und Enddatum)
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=fiscal_start,  # Standard: frühestes Datum in den Daten
        end_date=fiscal_end,    # Standard: spätestes Datum in den Daten
        display_format='YYYY-MM-DD'
    ),

    # Gauge Diagramm
    dcc.Graph(id='gauge-content'),

    # Balkendiagramm
    dcc.Graph(id='graph-content')
])

# Callback zur Aktualisierung der Graphen basierend auf der Datumsauswahl
@callback(
    Output('gauge-content', 'figure'),
    Output('graph-content', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_graphs(start_date, end_date):
    # Sicherstellen, dass das Datum als Datetime-Objekt verwendet wird
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Daten nach dem gewählten Zeitraum filtern
    df_filtered = dfFaktura[(dfFaktura['ProTime-Datum'] >= start_date) & (dfFaktura['ProTime-Datum'] <= end_date)]

    # Gruppieren nach 'Auftrag/Projekt/Kst.' und 'Positionsbezeichnung', dann 'Erfasste Menge' summieren
    df_grouped = df_filtered.groupby(['Auftrag/Projekt/Kst.', 'Positionsbezeichnung'], as_index=False)[
        'Erfasste Menge'].sum()

    # Summe durch 8 teilen, um PT zu erhalten
    df_grouped['Erfasste Menge'] = df_grouped['Erfasste Menge'] / 8

    # Gauge Diagramm erstellen
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=df_grouped['Erfasste Menge'].sum(),
        delta={'reference': 160},
        title={'text': "Faktura Total"},
        gauge={'axis': {'range': [0, 160]}},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    # Balkendiagramm erstellen
    bar_fig = px.bar(df_grouped, x='Positionsbezeichnung', y='Erfasste Menge',
                     title=f'Faktura nach Position ({start_date.date()} - {end_date.date()})')

    return gauge_fig, bar_fig


# App starten
if __name__ == '__main__':
    app.run(debug=True)
