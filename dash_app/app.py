from dash import Dash, html, dcc, Input, Output
import layout
import plotly.io as pio

from charts.faktura_gauge import callbacks as faktura_callbacks
from charts.projects_bar import callbacks as projects_callbacks
from charts.burndown_bar import callbacks as burndown_callbacks
from charts.overview_bar import callbacks as overview_callbacks
from charts.verhaeltnis_pie import callbacks as verhaeltnis_callbacks
from charts.ueberstunden_gauge import callbacks as ueberstunden_callbacks
from charts.faktura_ueberstunden_gauge import (
    callbacks as faktura_ueberstunden_callbacks,
)
from charts.wertschoepfend_gauge import callbacks as wertschoepfend_callbacks
from charts.faktura_wertschoepfend_pie import (
    callbacks as faktura_wertschoepfend_pie_callbacks,
)

from interactions import callbacks as interaction_callbacks

external_scripts = [
    {"src": "https://cdn.tailwindcss.com"},
]

pio.templates.default = "plotly_white"

app = Dash(external_scripts=external_scripts)

# Define the app layout with page content container
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Register callbacks
faktura_callbacks.register_callbacks(app)
projects_callbacks.register_callbacks(app)
burndown_callbacks.register_callbacks(app)
overview_callbacks.register_callbacks(app)
verhaeltnis_callbacks.register_callbacks(app)
faktura_wertschoepfend_pie_callbacks.register_callbacks(app)
interaction_callbacks.register_callbacks(app)
ueberstunden_callbacks.register_callbacks(app)
faktura_ueberstunden_callbacks.register_callbacks(app)
wertschoepfend_callbacks.register_callbacks(app)


# Callback for multi-page routing
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/help":
        from help_layout import create_layout as help_create_layout

        return help_create_layout()
    else:
        return layout.create_layout()


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
        dev_tools_props_check=False,
    )
