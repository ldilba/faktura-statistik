from dash import Dash
import layout
import callbacks
import dash_bootstrap_components as dbc

# Dash App initialisieren
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout importieren
app.layout = layout.create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app)

# App starten
if __name__ == '__main__':
    app.run_server(debug=True)
