from dash import Output, Input
from dash_app.charts.overview_bar import processing


def register_callbacks(app):
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
    )
    def update_interval_bar_chart(start_date, end_date, interval):
        figure = processing.create_interval_bar_chart(start_date, end_date, interval)
        return figure
