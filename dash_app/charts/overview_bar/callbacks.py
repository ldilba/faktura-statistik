from dash import Output, Input, State
from charts.overview_bar import processing
from common import charts, utils


def register_callbacks(app):
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Output("interval-bar-chart", "config"),
        Input("update-date-range", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_interval_bar_chart(
        _,
        interval,
        data_all,
        start_date,
        end_date,
    ):
        df_all = utils.deserialize_store_data(data_all, "all")
        if df_all is None:
            return charts.empty_figure(), {}
        figure, config = processing.create_interval_bar_chart(
            df_all, start_date, end_date, interval
        )
        return figure, config
