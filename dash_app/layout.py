from dash import html, dcc

import data_processing


def create_layout():
    """Erstellt das Dash-Layout."""
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return html.Div(
        [
            html.Div(
                [
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        start_date=fiscal_start,
                        end_date=fiscal_end,
                        display_format="YYYY-MM-DD",
                    )
                ], className="flex justify-center mt-4"
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="faktura-total-content", className="rounded-xl bg-white shadow-lg w-1/6"
                    )
                ],
                className="mx-5 flex",
            ),
            html.Div([
                html.Div(
                    [
                        dcc.Graph(
                            id="faktura-projekt-content", className="rounded-xl bg-white shadow-lg w-full"
                        )
                    ],
                    className="flex w-1/2",
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="burndown-content", className="rounded-xl bg-white shadow-lg w-full"
                        )
                    ],
                    className="flex w-1/2",
                )
            ], className="flex w-full gap-5 px-5"),

        ],
        className="w-full h-screen bg-slate-100 flex flex-col gap-4",
    )
