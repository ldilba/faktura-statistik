from dash import html, dcc
import data_processing


def create_layout():
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return html.Div(
        [
            # Datumsbereich
            html.Div(
                [
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        start_date=fiscal_start,
                        end_date=fiscal_end,
                        display_format="YYYY-MM-DD",
                    )
                ],
                className="flex justify-center mt-4",
            ),
            # Bestehende Graphen
            html.Div(
                [
                    dcc.Graph(
                        id="faktura-total-content",
                        className="rounded-xl bg-white shadow-lg w-1/6",
                    )
                ],
                className="mx-5 flex",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="faktura-projekt-content",
                                className="rounded-xl bg-white shadow-lg w-full",
                            )
                        ],
                        className="flex w-1/2",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="hours-burndown-content",
                                className="rounded-xl bg-white shadow-lg w-full",
                            )
                        ],
                        className="flex w-1/2",
                    ),
                ],
                className="flex w-full gap-5 px-5",
            ),
            # Neuer Bereich: Dropdown zur Auswahl der Aggregation und der neue Graph
            html.Div(
                [
                    html.Label("Aggregation:", className="font-semibold"),
                    dcc.Dropdown(
                        id="interval-dropdown",
                        options=[
                            {"label": "Tag", "value": "D"},
                            {"label": "Woche", "value": "W"},
                            {"label": "Monat", "value": "ME"},
                        ],
                        value="D",
                        clearable=False,
                        className="w-1/4",
                    ),
                ],
                className="mx-5 mt-4",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="interval-bar-chart",
                        className="rounded-xl bg-white shadow-lg",
                    )
                ],
                className="mx-5 mt-2",
            ),
        ],
        className="w-full bg-slate-100 flex flex-col gap-4 pb-5",
    )
