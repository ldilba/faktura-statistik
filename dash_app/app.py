from dash import Dash
import layout
import callbacks

# Dash App initialisieren
app = Dash()

# Layout importieren
app.layout = layout.create_layout()

# Callbacks registrieren
callbacks.register_callbacks(app)

# App starten
if __name__ == '__main__':
    app.run_server(debug=True)
