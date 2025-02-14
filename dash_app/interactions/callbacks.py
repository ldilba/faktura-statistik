import base64
import io

import pandas as pd
from dash import Output, Input

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
            df_all, df_faktura = data.import_data(df)
            return {"all": df_all.to_json(), "faktura": df_faktura.to_json()}

        except Exception as e:
            print(e)
            return None
