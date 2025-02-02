from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash()

df = pd.read_excel("export20250202192827.xlsx")

# Filtern: Keine NaN-Werte in 'Auftrag/Projekt/Kst.' und nur Werte, die mit 'K' oder 'X' starten
dfFaktura = df[df['Auftrag/Projekt/Kst.'].notna() & df['Auftrag/Projekt/Kst.'].str.startswith(('K', 'X'))][
    ['ProTime-Datum', 'Erfasste Menge', 'Auftrag/Projekt/Kst.', 'Positionsbezeichnung']]

# Gruppieren nach 'Auftrag/Projekt/Kst.' und 'Positionsbezeichnung', dann 'Erfasste Menge' summieren
dfFaktura_grouped = dfFaktura.groupby(['Auftrag/Projekt/Kst.', 'Positionsbezeichnung'], as_index=False)[
    'Erfasste Menge'].sum()

# Summe durch 8 teilen, um PT zu erhalten
dfFaktura_grouped['Erfasste Menge'] = dfFaktura_grouped['Erfasste Menge'] / 8

# print(dfFaktura)

app.layout = [
    html.H1(children='Dash App', style={'textAlign': 'center'}),
    dcc.Graph(figure=go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dfFaktura_grouped['Erfasste Menge'].sum(),
        delta={'reference': 160},
        title={'text': "Faktura Total"},
        gauge={
            'axis': {'range': [0, 160]}
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))),
    dcc.Graph(id='graph-content', figure=px.bar(dfFaktura_grouped, x='Positionsbezeichnung', y='Erfasste Menge'))
]


if __name__ == '__main__':
    app.run(debug=True)
