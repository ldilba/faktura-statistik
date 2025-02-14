from io import StringIO

from dash import Output, Input
from charts.overview_bar import processing
from common import charts
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
    )
    def update_interval_bar_chart(start_date, end_date, interval, data_all):
        if not data_all:
            return charts.empty_figure()

        df_all = pd.read_json(StringIO(data_all))
        figure = processing.create_interval_bar_chart(
            df_all, start_date, end_date, interval
        )
        return figure
