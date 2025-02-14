from io import StringIO

from dash import Output, Input, State
from common import data, charts
from charts.faktura_gauge import processing

import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("faktura-total-content", "figure"),
        Output("faktura-total-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_gauge_chart(_, data_all, start_date, end_date):
        if not data_all or not data_all["faktura"]:
            return charts.empty_figure(), {}

        df_faktura = pd.read_json(StringIO(data_all["faktura"]))
        df_grouped = data.filter_data_by_date(df_faktura, start_date, end_date)
        figure, config = processing.create_gauge_chart(df_grouped)
        return figure, config

    @app.callback(
        Output("faktura-daily-avg-pt-content", "figure"),
        Output("faktura-daily-avg-pt-content", "config"),
        Output("faktura-daily-avg-hours-content", "figure"),
        Output("faktura-daily-avg-hours-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_daily_average(_, interval, data_all, start_date, end_date):
        if not data_all or not data_all["faktura"] or not data_all["all"]:
            return charts.empty_figure(), {}, charts.empty_figure(), {}

        df_faktura = pd.read_json(StringIO(data_all["faktura"]))
        df_all = pd.read_json(StringIO(data_all["all"]))

        fig_pt, config_pt, fig_hours, config_hours = (
            processing.create_daily_average_indicators(
                df_faktura, df_all, start_date, end_date, interval
            )
        )
        return fig_pt, config_pt, fig_hours, config_hours
