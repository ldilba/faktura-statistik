from dash import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import data_processing


def register_callbacks(app):
    """Registriert die Callbacks für die Dash-App."""

    @app.callback(
        Output("gauge-content", "figure"),
        Output("graph-content", "figure"),
        Output("gauge-content", "config"),
        Output("graph-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_graphs(start_date, end_date):
        df = data_processing.load_and_clean_data()
        df_grouped = data_processing.filter_data_by_date(df, start_date, end_date)

        # Gauge Diagramm erstellen
        gauge_fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=df_grouped["Erfasste Menge"].sum(),
                delta={"reference": 160},
                title={"text": "Faktura Total"},
                gauge={"axis": {"range": [0, 160]}},
                domain={"x": [0, 1], "y": [0, 1]},
            )
        )

        config = {"staticPlot": True}

        gauge_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")

        gauge_fig.update_layout(
            height=225,  margin=dict(t=25, l=50, r=50, b=0)
        )

        # Balkendiagramm erstellen
        bar_fig = px.bar(
            df_grouped,
            x="Kurztext",
            y="Erfasste Menge",
            title=f"Tage Faktura nach Projekt",
            labels={"Kurztext": "Projekt"},
            template="plotly_white",
        )

        bar_fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")

        bar_fig.update_traces(texttemplate="%{y:.2f} PT", textposition="auto")

        return gauge_fig, bar_fig, config, config
