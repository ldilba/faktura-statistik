from io import StringIO

from dash import Output, Input, State
from charts.burndown_bar import processing
from common import charts

import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Output("hours-burndown-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("faktura-tage", "value"),
    )
    def update_hours_burndown(
        _, __, interval, data_all, start_date, end_date, faktura_tage
    ):
        if not data_all or not data_all["faktura"] or not data_all["all"]:
            return charts.empty_figure(), {}

        df_faktura = pd.read_json(StringIO(data_all["faktura"]))
        df_all = pd.read_json(StringIO(data_all["all"]))

        figure, config = processing.create_hours_burndown_chart(
            df_faktura, df_all, start_date, end_date, interval, int(faktura_tage)
        )
        return figure, config
