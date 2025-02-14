from dash import html, dcc
from dash_iconify import DashIconify
from common import data


def create_layout():
    fiscal_start, fiscal_end = data.get_fiscal_year_range()

    return html.Div(
        [
            dcc.Store(id="data-all"),
            # Datumsbereich
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(
                                    [
                                        "Drag and Drop or ",
                                        html.A(
                                            "Select File",
                                            className="text-blue-500",
                                        ),
                                    ]
                                ),
                                className="w-[250px] text-center py-3 cursor-pointer",
                                accept=".xlsx",
                            )
                        ],
                        className="flex items-center border border-dashed border-slate-300 hover:bg-slate-200 hover:border-blue-500 rounded-md",
                    ),
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="date-picker-range",
                                start_date=fiscal_start,
                                end_date=fiscal_end,
                                display_format="DD.MM.YYYY",
                            ),
                            html.Button(
                                DashIconify(
                                    icon="heroicons:arrow-path",
                                    height=24,
                                    color="#2B7FFF",
                                ),
                                id="update-date-range",
                                className="w-11 h-11 bg-white rounded-md flex items-center justify-center shadow-md hover:bg-slate-200",
                            ),
                        ],
                        className="flex gap-3 items-center",
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="interval-dropdown",
                                options=[
                                    {"label": "Tag", "value": "D"},
                                    {"label": "Woche", "value": "W"},
                                    {"label": "Monat", "value": "ME"},
                                ],
                                value="D",
                                clearable=False,
                                className="w-[250px]",
                            ),
                        ],
                        className="flex",
                    ),
                ],
                className="flex justify-between items-center mt-4 mx-5",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="faktura-total-content",
                        className="rounded-xl bg-white shadow-lg w-1/6 h-[14rem]",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="faktura-daily-avg-pt-content",
                                className="rounded-xl bg-white shadow-lg h-[6.5rem]",
                            ),
                            dcc.Graph(
                                id="faktura-daily-avg-hours-content",
                                className="rounded-xl bg-white shadow-lg h-[6.5rem]",
                            ),
                        ],
                        className="flex flex-col gap-4 w-1/6",
                    ),
                ],
                className="flex mx-5 gap-5",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="hours-burndown-content",
                        className="rounded-xl bg-white shadow-lg w-full",
                    )
                ],
                className="flex mx-5",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="faktura-projekt-content",
                                className="rounded-xl bg-white shadow-lg",
                            )
                        ],
                        className="w-full min-w-0",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="interval-bar-chart",
                                className="rounded-xl bg-white shadow-lg",
                            )
                        ],
                        className="w-full min-w-0",
                    ),
                ],
                className="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-5 px-5 w-full",
            ),
        ],
        className="w-full bg-slate-100 flex flex-col gap-4 pb-5",
    )
