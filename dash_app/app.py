from dash import Dash
import layout
import plotly.io as pio

from charts.faktura_gauge import callbacks as faktura_callbacks
from charts.projects_bar import callbacks as projects_callbacks
from charts.burndown_bar import callbacks as burndown_callbacks
from charts.overview_bar import callbacks as overview_callbacks
from charts.verhaeltnis_pie import callbacks as verhaeltnis_callbacks
from charts.ueberstunden_gauge import callbacks as ueberstunden_callbacks

from interactions import callbacks as interaction_callbacks

external_scripts = [
    {"src": "https://cdn.tailwindcss.com"},
]

pio.templates.default = "plotly_white"

app = Dash(external_scripts=external_scripts)

app.layout = layout.create_layout()

faktura_callbacks.register_callbacks(app)
projects_callbacks.register_callbacks(app)
burndown_callbacks.register_callbacks(app)
overview_callbacks.register_callbacks(app)
verhaeltnis_callbacks.register_callbacks(app)
interaction_callbacks.register_callbacks(app)
ueberstunden_callbacks.register_callbacks(app)

server = app.server


@server.route("/healthz")
def healthz():
    return "OK", 200


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        port=8050,
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False
    )
