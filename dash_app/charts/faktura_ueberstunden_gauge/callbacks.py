from dash import Output, Input, State
from charts.faktura_ueberstunden_gauge import processing
from common import data, charts, utils


def register_callbacks(app):
    @app.callback(
        Output("faktura-ueberstunden-content", "figure"),
        Output("faktura-ueberstunden-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_faktura_gauge_chart(_, data_all, start_date, end_date):
        df_all = utils.deserialize_store_data(data_all, "all")
        if df_all is None:
            return charts.empty_figure(), {}
        figure, config = processing.create_faktura_ueberstunden_chart(
            df_all, start_date, end_date
        )
        return figure, config
