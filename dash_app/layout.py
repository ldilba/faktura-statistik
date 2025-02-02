from dash import html, dcc
import data_processing


def create_layout():
    """Erstellt das Dash-Layout."""
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return html.Div([
        html.H1(children='Dash App', style={'textAlign': 'center'}),

        # Datumsauswahl (Start- und Enddatum)
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=fiscal_start,
            end_date=fiscal_end,
            display_format='YYYY-MM-DD'
        ),

        # Gauge Diagramm
        dcc.Graph(id='gauge-content'),

        # Balkendiagramm
        dcc.Graph(id='graph-content')
    ])
