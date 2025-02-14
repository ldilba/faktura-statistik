from io import StringIO

from dash import Output, Input
from charts.burndown_bar import processing
from common import charts

import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
        Input("data-faktura", "data"),
        Input("data-all", "data"),
    )
    def update_hours_burndown(start_date, end_date, interval, data_faktura, data_all):
        if not data_faktura:
            return charts.empty_figure()

        df_faktura = pd.read_json(StringIO(data_faktura))
        df_all = pd.read_json(StringIO(data_all))

        figure = processing.create_hours_burndown_chart(
            df_faktura, df_all, start_date, end_date, interval
        )
        return figure
