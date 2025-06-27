import base64
import io
import json

import pandas as pd
from dash import Output, Input, State

from common import data


def register_callbacks(app):
    @app.callback(
        Output("data-all", "data"),
        Input("upload-data", "contents"),
    )
    def update_output(contents):

        if contents is None:
            return None

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            df = pd.read_excel(io.BytesIO(decoded))
            df_all, df_faktura, df_wertschoepfend = data.import_data(df)
            return {
                "all": df_all.to_json(), 
                "faktura": df_faktura.to_json(),
                "wertschoepfend": df_wertschoepfend.to_json()
            }

        except Exception as e:
            print(e)
            return None

    @app.callback(
        Output("faktura-tage", "value"),
        Output("wertschoepfend-tage", "value"),
        Input("update-faktura-tage", "n_clicks"),
        State("faktura-tage", "value"),
        State("wertschoepfend-tage", "value"),
    )
    def update_target_values(n_clicks, faktura_target, wertschoepfend_target):
        if n_clicks is None:
            return faktura_target, wertschoepfend_target

        # Simply return the current values without updating config.json
        # The config.json is only used for initial loading
        return faktura_target, wertschoepfend_target
