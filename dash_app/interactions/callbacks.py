import base64
import io
import json

import pandas as pd
from dash import Output, Input, State, no_update

from common import data, utils
from common.constants import REQUIRED_COLUMNS


def register_callbacks(app):
    @app.callback(
        Output("settings-container", "style"),
        Input("settings-button", "n_clicks"),
        State("settings-container", "style"),
        prevent_initial_call=True,
    )
    def toggle_settings(n_clicks, current_style):
        if current_style.get("display") == "none":
            return {"display": "flex"}
        else:
            return {"display": "none"}

    @app.callback(
        Output("data-all", "data"),
        Output("toast-data", "data"),
        Output("upload-error-message", "children"),
        Input("upload-data", "contents"),
    )
    def update_output(contents):
        # Clear error message when no file is uploaded
        if contents is None:
            return None, {"message": "", "is_open": False}, ""

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            # Try to read the Excel file
            df = pd.read_excel(io.BytesIO(decoded))

            # Validate required columns
            error_msg = utils.validate_required_columns(df, REQUIRED_COLUMNS)
            if error_msg:
                return utils.create_error_response(error_msg)

            # Process the data
            df_all, df_faktura, df_wertschoepfend = data.import_data(df)

            return (
                {
                    "all": df_all.to_json(),
                    "faktura": df_faktura.to_json(),
                    "wertschoepfend": df_wertschoepfend.to_json(),
                },
                {"message": "", "is_open": False},
                "",
            )

        except pd.errors.EmptyDataError:
            return utils.create_error_response(
                "Die hochgeladene Datei enthält keine Daten."
            )
        except pd.errors.ParserError:
            return utils.create_error_response(
                "Die Datei konnte nicht gelesen werden. Bitte überprüfen Sie das Format."
            )
        except Exception as e:
            print(e)
            return utils.create_error_response(f"Ein Fehler ist aufgetreten: {str(e)}")

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

    @app.callback(
        Output("resturlaub-input", "value"),
        Input("update-resturlaub", "n_clicks"),
        State("resturlaub-input", "value"),
    )
    def update_resturlaub_value(n_clicks, resturlaub_value):
        if n_clicks is None:
            return resturlaub_value

        # Simply return the current value to trigger update of dependent components
        return resturlaub_value
