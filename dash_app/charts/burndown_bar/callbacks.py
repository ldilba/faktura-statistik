from dash import Output, Input, no_update
from charts.burndown_bar import processing
from common import charts


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
        Input("update-trigger", "data"),
        Input("data-loaded", "data"),
    )
    def update_hours_burndown(start_date, end_date, interval, update, data_loaded):
        if not data_loaded:
            return charts.empty_figure()

        if not update:
            return no_update

        figure = processing.create_hours_burndown_chart(start_date, end_date, interval)
        return figure
