from dash import html, dcc

# import dash_bootstrap_components as dbc
import data_processing


def create_layout():
    """Erstellt das Dash-Layout."""
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return html.Div(
        [
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date=fiscal_start,
                end_date=fiscal_end,
                display_format="YYYY-MM-DD",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="gauge-content", className="!rounded-xl bg-white shadow-lg"
                    )
                ],
                className="mx-5 flex",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="graph-content", className="!rounded-xl bg-white shadow-lg"
                    )
                ],
                className="mx-5 flex",
            ),
        ],
        className="w-full h-screen bg-slate-100 flex flex-col gap-4",
    )
