from io import StringIO

from dash import Output, Input, State
from charts.overview_bar import processing
from common import charts
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("update-date-range", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_interval_bar_chart(
        _,
        interval,
        data_all,
        start_date,
        end_date,
    ):
        if not data_all or not data_all["all"]:
            return charts.empty_figure()

        df_all = pd.read_json(StringIO(data_all["all"]))
        figure = processing.create_interval_bar_chart(
            df_all, start_date, end_date, interval
        )
        return figure
