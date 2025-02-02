from dash import html, dcc
import dash_bootstrap_components as dbc
import data_processing


def create_layout():
    """Erstellt das Dash-Layout."""
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return dbc.Container([
        # Überschrift links
        dbc.Row([
            dbc.Col(html.H2("Faktura Statistics"), width=4),
            dbc.Col(
                html.Div(
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=fiscal_start,
                        end_date=fiscal_end,
                        display_format='YYYY-MM-DD',
                    ),
                    className="d-flex justify-content-center"
                ),
                width=4
            ),
            dbc.Col(width=4),
        ], className="mb-3 mt-3 mx-3", justify='between'),

        # Graphen unter dem DatePicker
        dbc.Row([
            dbc.Col(dcc.Graph(id='gauge-content'), width=12)
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-content'), width=12)
        ])
    ], fluid=True)

