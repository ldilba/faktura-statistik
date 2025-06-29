from io import StringIO

from dash import Output, Input, State
from charts.burndown_bar import processing
from common import charts

import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("wertschoepfend-tage", "value"),
    )
    def update_hours_burndown(
        _, __, interval, data_all, start_date, end_date, wertschoepfend_tage
    ):
        if not data_all or not data_all["wertschoepfend"] or not data_all["all"]:
            return charts.empty_figure()

        df_wertschoepfend = pd.read_json(StringIO(data_all["wertschoepfend"]))
        df_all = pd.read_json(StringIO(data_all["all"]))

        figure = processing.create_hours_burndown_chart(
            df_wertschoepfend,
            df_all,
            start_date,
            end_date,
            interval,
            float(wertschoepfend_tage),
        )
        return figure
