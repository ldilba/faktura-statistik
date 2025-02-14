from io import StringIO

from dash import Output, Input
from common import data, charts
from charts.projects_bar import processing
import pandas as pd


def register_callbacks(app):
    @app.callback(
        Output("faktura-projekt-content", "figure"),
        Output("faktura-projekt-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("data-faktura", "data"),
        prevent_initial_call=True,
    )
    def update_project_bar(start_date, end_date, data_faktura):
        if not data_faktura:
            return charts.empty_figure(), {"staticPlot": True}

        df = pd.read_json(StringIO(data_faktura))

        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_project_bar_chart(df_grouped)
        return figure, config
