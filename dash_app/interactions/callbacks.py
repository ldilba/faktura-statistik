import base64
import io
import json

import pandas as pd
from dash import Output, Input, State, no_update

from common import data


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

            # Define required columns
            required_columns = [
                "Auftrag/Projekt/Kst.",
                "Leistung",
                "ProTime-Datum",
                "Erfasste Menge",
                "Kurztext",
                "Positionsbezeichnung",
            ]

            # Check if all required columns are present
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                # Return error message with missing columns
                error_msg = (
                    f"Fehlende Spalten in der Datei: {', '.join(missing_columns)}"
                )
                return None, {"message": error_msg, "is_open": True}, ""

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
            error_msg = "Die hochgeladene Datei enthält keine Daten."
            return None, {"message": error_msg, "is_open": True}, ""
        except pd.errors.ParserError:
            error_msg = "Die Datei konnte nicht gelesen werden. Bitte überprüfen Sie das Format."
            return None, {"message": error_msg, "is_open": True}, ""
        except Exception as e:
            print(e)
            error_msg = f"Ein Fehler ist aufgetreten: {str(e)}"
            return None, {"message": error_msg, "is_open": True}, ""

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
