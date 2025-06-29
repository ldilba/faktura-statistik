from io import StringIO

from dash import Output, Input, State

from charts.faktura_wertschoepfend_pie import processing
from common import data, charts
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("faktura-wertschoepfend-pie-content", "figure"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_faktura_wertschoepfend_pie(_, data_all, start_date, end_date):
        if (
            not data_all
            or not data_all["all"]
            or not data_all["faktura"]
            or not data_all["wertschoepfend"]
        ):
            return charts.empty_figure()

        df_all = pd.read_json(StringIO(data_all["all"]))
        df_faktura = pd.read_json(StringIO(data_all["faktura"]))
        df_wertschoepfend = pd.read_json(StringIO(data_all["wertschoepfend"]))

        # Filter data by date
        df_all_filtered = data.filter_data_by_date(df_all, start_date, end_date)
        df_faktura_filtered = data.filter_data_by_date(df_faktura, start_date, end_date)
        df_wertschoepfend_filtered = data.filter_data_by_date(
            df_wertschoepfend, start_date, end_date
        )

        figure = processing.create_faktura_wertschoepfend_pie_chart(
            df_faktura_filtered, df_wertschoepfend_filtered, df_all_filtered
        )
        return figure
