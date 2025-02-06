from dash import Output, Input
from dash_app.common import data
from dash_app.charts.projects_bar import processing


def register_callbacks(app):
    @app.callback(
        Output("faktura-projekt-content", "figure"),
        Output("faktura-projekt-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_project_bar(start_date, end_date):
        df = data.df_faktura.copy()
        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_project_bar_chart(df_grouped)
        return figure, config
