from dash import Output, Input
from dash_app.charts.burndown_bar import processing


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
    )
    def update_hours_burndown(start_date, end_date, interval):
        figure = processing.create_hours_burndown_chart(start_date, end_date, interval)
        return figure
