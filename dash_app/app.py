from dash import Dash
import layout
import callbacks

external_scripts = [{"src": "https://cdn.tailwindcss.com"}]

# Dash App initialisieren
app = Dash(external_scripts=external_scripts)

# Layout importieren
app.layout = layout.create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app)

# App starten
if __name__ == "__main__":
    app.run_server(debug=True)
