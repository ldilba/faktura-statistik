from dash import html, dcc
import data_processing


def create_layout():
    fiscal_start, fiscal_end = data_processing.get_fiscal_year_range()

    return html.Div(
        [
            # Datumsbereich
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(
                                    ["Drag and Drop or ", html.A("Select File")]
                                ),
                                className="w-[250px] text-center py-3 cursor-pointer",
                                accept=".xlsx",
                            )
                        ],
                        className="flex items-center border border-dashed border-slate-300 hover:border-slate-700 rounded-md",
                    ),
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        start_date=fiscal_start,
                        end_date=fiscal_end,
                        display_format="YYYY-MM-DD",
                    ),
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
                className="flex justify-around items-center mt-4 ",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="faktura-total-content",
                        className="rounded-xl bg-white shadow-lg w-1/6",
                    )
                ],
                className="flex mx-5",
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
                        className="w-full",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="interval-bar-chart",
                                className="rounded-xl bg-white shadow-lg",
                            )
                        ],
                        className="w-full",
                    ),
                ],
                className="grid grid-cols-[1fr_2fr] gap-5 px-5 w-full",
            ),
        ],
        className="w-full bg-slate-100 flex flex-col gap-4 pb-5",
    )
