from dash import Dash
import layout
import plotly.io as pio

from charts.faktura_gauge import callbacks as faktura_callbacks
from charts.projects_bar import callbacks as projects_callbacks
from charts.burndown_bar import callbacks as burndown_callbacks
from charts.overview_bar import callbacks as overview_callbacks

from interactions import callbacks as interaction_callbacks

external_scripts = [
    {"src": "https://cdn.tailwindcss.com"},
    {"src": "https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"},
]

pio.templates.default = "plotly_white"

app = Dash(external_scripts=external_scripts)

app.layout = layout.create_layout()

faktura_callbacks.register_callbacks(app)
projects_callbacks.register_callbacks(app)
burndown_callbacks.register_callbacks(app)
overview_callbacks.register_callbacks(app)
interaction_callbacks.register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
