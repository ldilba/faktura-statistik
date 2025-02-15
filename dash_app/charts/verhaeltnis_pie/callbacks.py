from io import StringIO

from dash import Output, Input, State

from charts.verhaeltnis_pie import processing
from common import data, charts
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("verhaeltnis-pie-content", "figure"),
        Output("verhaeltnis-pie-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_verhaeltnis_pie(_, data_all, start_date, end_date):
        if not data_all or not data_all["all"]:
            return charts.empty_figure(), {}

        df = pd.read_json(StringIO(data_all["all"]))

        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_verhaeltnis_pie_chart(df_grouped)
        return figure, config
