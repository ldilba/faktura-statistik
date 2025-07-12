from dash import Output, Input, State
from common import data, charts, utils
from charts.projects_bar import processing


def register_callbacks(app):
    @app.callback(
        Output("faktura-projekt-content", "figure"),
        Output("faktura-projekt-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_project_bar(_, data_all, start_date, end_date):
        df = utils.deserialize_store_data(data_all, "faktura")
        if df is None:
            return charts.empty_figure(), {}

        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_project_bar_chart(df_grouped)
        return figure, config
