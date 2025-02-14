from dash import Output, Input
from common import data, charts
from charts.projects_bar import processing


def register_callbacks(app):
    @app.callback(
        Output("faktura-projekt-content", "figure"),
        Output("faktura-projekt-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("data-loaded", "data"),
    )
    def update_project_bar(start_date, end_date, data_loaded):
        print(data_loaded)
        if not data_loaded:
            return charts.empty_figure(), {}

        df = data.df_faktura.copy()
        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_project_bar_chart(df_grouped)
        return figure, config
