from io import StringIO

from dash import Output, Input, State

from charts.ueberstunden_gauge import processing
from common import data, charts
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("ueberstunden-content", "figure"),
        Output("ueberstunden-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_gauge_chart(_, data_all, start_date, end_date):
        if not data_all or not data_all["all"]:
            return charts.empty_figure(), {}

        df_all = pd.read_json(StringIO(data_all["all"]))
        figure, config = processing.create_verhaeltnis_chart(
            df_all, start_date, end_date
        )
        return figure, config
