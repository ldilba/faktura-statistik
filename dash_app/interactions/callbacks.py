import base64
import io

import pandas as pd
from dash import Output, Input, State, html, callback_context

from common import data


def register_callbacks(app):
    @app.callback(
        Output("output-data-upload", "children"),
        Output("clear-message-interval", "disabled"),
        Output("data-loaded", "data"),
        Input("upload-data", "contents"),
        Input("clear-message-interval", "n_intervals"),
        State("upload-data", "filename"),
    )
    def update_output(contents, n_intervals, filename):
        ctx = callback_context
        trigger_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )

        # Falls Timer ausgelöst wurde, lösche die Nachricht
        if trigger_id == "clear-message-interval":
            return "", True, True

        if contents is None:
            return "", True, False

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            # Datei als DataFrame laden
            df = pd.read_excel(io.BytesIO(decoded))

            # save_path = f"data/{filename}"
            # os.makedirs("data", exist_ok=True)
            # with open(save_path, "wb") as f:
            #     f.write(decoded)

            data.import_data(df)
            # os.remove(save_path)

            return (
                html.Div("Datei hochgeladen.", className="text-green-500"),
                False,
                True,
            )

        except Exception as e:

            return (
                html.Div("Fehler beim hochladen.", className="text-red-500"),
                True,
                False,
            )
