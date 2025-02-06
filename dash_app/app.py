# app.py
from dash import Dash
import layout

# Importiere die Callback-Registrierungsfunktionen der einzelnen Chart-Module:
from charts.faktura_gauge import callbacks as faktura_callbacks
from charts.projects_bar import callbacks as projects_callbacks
from charts.burndown_bar import callbacks as burndown_callbacks
from charts.overview_bar import callbacks as overview_callbacks
from dash_app.common import data

from interactions import callbacks as interaction_callbacks

# Optionale externe Skripte (hier z. B. TailwindCSS)
external_scripts = [{"src": "https://cdn.tailwindcss.com"}]

# Dash-App initialisieren
app = Dash(external_scripts=external_scripts)

# Layout setzen (das Layout kannst du natürlich auch modular aufteilen)
app.layout = layout.create_layout()

# Registriere die Callbacks aller Charts:
faktura_callbacks.register_callbacks(app)
projects_callbacks.register_callbacks(app)
burndown_callbacks.register_callbacks(app)
overview_callbacks.register_callbacks(app)
interaction_callbacks.register_callbacks(app)

data.first_import(app)

if __name__ == "__main__":
    app.run_server(debug=True)
