from dash import Output, Input, State
from charts.burndown_bar import processing
from common import charts, utils


def register_callbacks(app):
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Output("hours-burndown-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("update-faktura-tage", "n_clicks"),
        Input("update-resturlaub", "n_clicks"),
        Input("interval-dropdown", "value"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
        State("wertschoepfend-tage", "value"),
        State("resturlaub-input", "value"),
    )
    def update_hours_burndown(
        _,
        __,
        ___,
        interval,
        data_all,
        start_date,
        end_date,
        wertschoepfend_tage,
        resturlaub_value,
    ):
        df_wertschoepfend = utils.deserialize_store_data(data_all, "wertschoepfend")
        df_all = utils.deserialize_store_data(data_all, "all")

        if df_wertschoepfend is None or df_all is None:
            return charts.empty_figure(), {}

        vacation_days = resturlaub_value if resturlaub_value is not None else 0
        figure, config = processing.create_hours_burndown_chart(
            df_wertschoepfend,
            df_all,
            start_date,
            end_date,
            interval,
            float(wertschoepfend_tage),
            int(vacation_days),
        )
        return figure, config
