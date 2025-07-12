from dash import Output, Input, State
from charts.faktura_wertschoepfend_pie import processing
from common import data, charts, utils


def register_callbacks(app):
    @app.callback(
        Output("faktura-wertschoepfend-pie-content", "figure"),
        Output("faktura-wertschoepfend-pie-content", "config"),
        Input("update-date-range", "n_clicks"),
        Input("data-all", "data"),
        State("date-picker-range", "start_date"),
        State("date-picker-range", "end_date"),
    )
    def update_faktura_wertschoepfend_pie(_, data_all, start_date, end_date):
        df_all = utils.deserialize_store_data(data_all, "all")
        df_faktura = utils.deserialize_store_data(data_all, "faktura")
        df_wertschoepfend = utils.deserialize_store_data(data_all, "wertschoepfend")

        if df_all is None or df_faktura is None or df_wertschoepfend is None:
            return charts.empty_figure(), {}

        # Filter data by date
        df_all_filtered = data.filter_data_by_date(df_all, start_date, end_date)
        df_faktura_filtered = data.filter_data_by_date(df_faktura, start_date, end_date)
        df_wertschoepfend_filtered = data.filter_data_by_date(
            df_wertschoepfend, start_date, end_date
        )

        figure, config = processing.create_faktura_wertschoepfend_pie_chart(
            df_faktura_filtered, df_wertschoepfend_filtered, df_all_filtered
        )
        return figure, config
