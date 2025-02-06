from dash import Output, Input, no_update
from dash_app.common import data, charts
from dash_app.charts.faktura_gauge import processing


def register_callbacks(app):
    @app.callback(
        Output("faktura-total-content", "figure"),
        Output("faktura-total-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("update-trigger", "data"),
        Input("data-loaded", "data"),
    )
    def update_gauge_chart(start_date, end_date, update, data_loaded):
        if not data_loaded:
            return charts.empty_figure(), {}

        if not update:
            return no_update

        df = data.df_faktura.copy()
        df_grouped = data.filter_data_by_date(df, start_date, end_date)
        figure, config = processing.create_gauge_chart(df_grouped)
        return figure, config

    @app.callback(
        Output("faktura-daily-avg-pt-content", "figure"),
        Output("faktura-daily-avg-pt-content", "config"),
        Output("faktura-daily-avg-hours-content", "figure"),
        Output("faktura-daily-avg-hours-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
        Input("update-trigger", "data"),
        Input("data-loaded", "data"),
    )
    def update_daily_average(start_date, end_date, interval, update, data_loaded):
        if not data_loaded:
            return charts.empty_figure(), {}, charts.empty_figure(), {}

        if not update:
            return no_update

        df_faktura = data.df_faktura.copy()
        df_all = data.df_all.copy()
        fig_pt, config_pt, fig_hours, config_hours = (
            processing.create_daily_average_indicators(
                df_faktura, df_all, start_date, end_date, interval
            )
        )
        return fig_pt, config_pt, fig_hours, config_hours
