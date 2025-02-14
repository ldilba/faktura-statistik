from dash import Output, Input
from charts.overview_bar import processing
from common import charts


def register_callbacks(app):
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
        Input("data-loaded", "data"),
    )
    def update_interval_bar_chart(start_date, end_date, interval, data_loaded):
        if not data_loaded:
            return charts.empty_figure()

        figure = processing.create_interval_bar_chart(start_date, end_date, interval)
        return figure
