from io import StringIO

from dash import Output, Input, State
from common import data, charts
from charts.wertschoepfend_gauge import processing

import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("wertschoepfend-total-content", "figure"),
        Output("wertschoepfend-total-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("wertschoepfend-tage", "value"),
    )
    def update_gauge_chart(_, __, data_all, start_date, end_date, wertschoepfend_tage):
        if not data_all or not data_all["wertschoepfend"]:
            return charts.empty_figure(), {}

        df_wertschoepfend = pd.read_json(StringIO(data_all["wertschoepfend"]))
        df_grouped = data.filter_data_by_date(df_wertschoepfend, start_date, end_date)
        figure, config = processing.create_gauge_chart(df_grouped, int(wertschoepfend_tage))
        return figure, config
