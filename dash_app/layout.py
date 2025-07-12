import json

from dash import (
    html,
    dcc,
    clientside_callback,
    ClientsideFunction,
    Output,
    Input,
    State,
)
from dash_iconify import DashIconify
from common import data


def load_config():
    try:
        with open("../config.json", "r") as file:
            config = json.load(file)
            return {
                "faktura_target": config.get("faktura_target", 160),
                "wertschoepfend_target": config.get("wertschoepfend_target", 193),
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {"faktura_target": 160, "wertschoepfend_target": 193}


config_values = load_config()
faktura_target = config_values["faktura_target"]
wertschoepfend_target = config_values["wertschoepfend_target"]


def register_clientside_callbacks(app):
    """Register clientside callbacks for the layout."""
    # Clientside callback for toast notifications
    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="update_toast"),
        Output("toast-container", "className"),
        Output("toast-message", "children"),
        Input("toast-data", "data"),
        Input("toast-close", "n_clicks"),
    )


def create_layout():
    fiscal_start, fiscal_end = data.get_fiscal_year_range()

    return html.Div(
        [
            dcc.Store(id="data-all"),
            dcc.Store(id="toast-data", data={"message": "", "is_open": False}),
            # Toast notification
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(id="toast-message"),
                            html.Button(
                                "×",
                                id="toast-close",
                                className="ml-2 text-white",
                                n_clicks=0,
                            ),
                        ],
                        className="flex justify-between items-center px-4 py-3 bg-red-500 text-white rounded-lg shadow-lg",
                    )
                ],
                id="toast-container",
                className="fixed top-4 right-4 z-50 transition-opacity duration-300 opacity-0 pointer-events-none",
            ),
            # Datumsbereich
            html.Div(
                [
                    html.Div(
                        [
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
                                                className="w-full sm:w-[250px] text-center py-2 cursor-pointer",
                                                accept=".xlsx",
                                            ),
                                            html.A(
                                                DashIconify(
                                                    icon="heroicons:question-mark-circle",
                                                    height=24,
                                                    color="#2B7FFF",
                                                ),
                                                href="/help",
                                                className="ml-2 p-1 hover:bg-slate-200 rounded-full",
                                                title="Hilfe",
                                            ),
                                        ],
                                        className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-0",
                                    )
                                ],
                                className="flex items-center border border-dashed border-slate-300 hover:bg-slate-200 hover:border-blue-500 rounded-md",
                            ),
                            html.Div(
                                id="upload-error-message",
                                className="text-red-500 text-sm mt-1 ml-2",
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
                                        className="w-10 h-10 bg-white rounded-md flex items-center justify-center shadow-md hover:bg-slate-200",
                                    ),
                                    html.Div(
                                        "Resturlaub (PT):",
                                        className="text-gray-700 ml-4",
                                    ),
                                    dcc.Input(
                                        value=0,
                                        id="resturlaub-input",
                                        className="p-2 rounded-md border border-gray-300 w-20",
                                        type="number",
                                        min=0,
                                        step=1,
                                    ),
                                    html.Button(
                                        DashIconify(
                                            icon="heroicons:arrow-path",
                                            height=24,
                                            color="#2B7FFF",
                                        ),
                                        id="update-resturlaub",
                                        className="w-10 h-10 bg-white rounded-md flex items-center justify-center shadow-md hover:bg-slate-200",
                                    ),
                                ],
                                className="flex flex-wrap gap-2 sm:gap-3 items-center",
                            ),
                        ],
                        className="flex flex-col lg:flex-row gap-3 lg:gap-6",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "Faktura Ziel PT:", className="text-gray-700"
                                    ),
                                    dcc.Input(
                                        value=faktura_target,
                                        id="faktura-tage",
                                        className="p-2 rounded-md border border-gray-300 w-20",
                                        type="number",
                                        step="0.01",
                                    ),
                                    html.Div(
                                        "Wertschöpfend Ziel PT:",
                                        className="text-gray-700 ml-2 sm:ml-4",
                                    ),
                                    dcc.Input(
                                        value=wertschoepfend_target,
                                        id="wertschoepfend-tage",
                                        className="p-2 rounded-md border border-gray-300 w-20",
                                        type="number",
                                        step="0.01",
                                    ),
                                    html.Button(
                                        DashIconify(
                                            icon="heroicons:arrow-path",
                                            height=24,
                                            color="#2B7FFF",
                                        ),
                                        id="update-faktura-tage",
                                        className="w-10 h-10 bg-white rounded-md flex items-center justify-center shadow-md hover:bg-slate-200",
                                    ),
                                ],
                                id="settings-container",
                                className="flex flex-wrap gap-2 sm:gap-3 items-center",
                                style={"display": "none"},
                            ),
                            html.Button(
                                DashIconify(
                                    icon="heroicons:cog-6-tooth",
                                    height=24,
                                    color="#2B7FFF",
                                ),
                                id="settings-button",
                                className="w-10 h-10 bg-white rounded-md flex items-center justify-center shadow-md hover:bg-slate-200 mr-2",
                                title="Einstellungen",
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
                                className="w-full sm:w-[250px]",
                            ),
                        ],
                        className="flex flex-col sm:flex-row gap-3 items-start sm:items-center",
                    ),
                ],
                className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mt-4 mx-5",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="faktura-total-content",
                        className="rounded-xl bg-white shadow-lg w-full sm:w-1/2 lg:w-1/5 xl:w-1/6 h-[14rem]",
                    ),
                    dcc.Graph(
                        id="wertschoepfend-total-content",
                        className="rounded-xl bg-white shadow-lg w-full sm:w-1/2 lg:w-1/5 xl:w-1/6 h-[14rem]",
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
                        className="flex flex-col gap-4 w-full sm:w-1/2 lg:w-1/5 xl:w-1/6",
                    ),
                    dcc.Graph(
                        id="ueberstunden-content",
                        className="rounded-xl bg-white shadow-lg w-full sm:w-1/2 lg:w-1/5 xl:w-1/6",
                    ),
                    dcc.Graph(
                        id="faktura-ueberstunden-content",
                        className="rounded-xl bg-white shadow-lg w-full sm:w-1/2 lg:w-1/5 xl:w-1/6",
                    ),
                ],
                className="flex flex-wrap justify-center lg:justify-start mx-5 gap-5",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="hours-burndown-content",
                        className="rounded-xl bg-white shadow-lg w-full",
                    )
                ],
                className="flex mx-5 mt-5",
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
                className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-5 px-5 w-full mt-5",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="verhaeltnis-pie-content",
                                className="rounded-xl bg-white shadow-lg",
                            )
                        ],
                        className="w-full lg:w-1/2",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="faktura-wertschoepfend-pie-content",
                                className="rounded-xl bg-white shadow-lg",
                            )
                        ],
                        className="w-full lg:w-1/2",
                    ),
                ],
                className="px-5 flex flex-col lg:flex-row gap-5 w-full lg:w-4/5 mt-5",
            ),
        ],
        className="w-full bg-slate-100 flex flex-col gap-4 pb-5",
    )
