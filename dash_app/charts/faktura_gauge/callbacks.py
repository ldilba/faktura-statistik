from dash import Output, Input, State
from common import data, charts, utils
from charts.faktura_gauge import processing


def register_callbacks(app):
    @app.callback(
        Output("faktura-total-content", "figure"),
        Output("faktura-total-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("faktura-tage", "value"),
    )
    def update_gauge_chart(_, __, data_all, start_date, end_date, faktura_tage):
        df_faktura = utils.deserialize_store_data(data_all, "faktura")
        if df_faktura is None:
            return charts.empty_figure(), {}

        df_grouped = data.filter_data_by_date(df_faktura, start_date, end_date)
        figure, config = processing.create_gauge_chart(df_grouped, float(faktura_tage))
        return figure, config

    @app.callback(
        Output("faktura-daily-avg-pt-content", "figure"),
        Output("faktura-daily-avg-pt-content", "config"),
        Output("faktura-daily-avg-hours-content", "figure"),
        Output("faktura-daily-avg-hours-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("update-resturlaub", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("faktura-tage", "value"),
        State("resturlaub-input", "value"),
    )
    def update_daily_average(
        _,
        __,
        ___,
        interval,
        data_all,
        start_date,
        end_date,
        faktura_tage,
        resturlaub_value,
    ):
        df_faktura = utils.deserialize_store_data(data_all, "faktura")
        df_all = utils.deserialize_store_data(data_all, "all")

        if df_faktura is None or df_all is None:
            return charts.empty_figure(), {}, charts.empty_figure(), {}

        vacation_days = resturlaub_value if resturlaub_value is not None else 0
        fig_pt, config_pt, fig_hours, config_hours = (
            processing.create_daily_average_indicators(
                df_faktura,
                df_all,
                start_date,
                end_date,
                interval,
                float(faktura_tage),
                int(vacation_days),
            )
        )
        return fig_pt, config_pt, fig_hours, config_hours
