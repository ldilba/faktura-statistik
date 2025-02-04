from dash import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import data_processing


def register_callbacks(app):
    """Registriert die Callbacks für die Dash-App."""

    @app.callback(
        Output("faktura-total-content", "figure"),
        Output("faktura-projekt-content", "figure"),
        Output("hours-overview-content", "figure"),
        Output("faktura-total-content", "config"),
        Output("faktura-projekt-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_graphs(start_date, end_date):
        # Für diese Diagramme arbeiten wir mit dem Faktura-DataFrame
        df = data_processing.df_full.copy()
        df_grouped = data_processing.filter_data_by_date(df, start_date, end_date)

        # Gauge-Diagramm erstellen
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
        gauge_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=225, margin=dict(t=25, l=50, r=50, b=0))

        # Balkendiagramm (Projektbezogen)
        bar_fig = px.bar(
            df_grouped,
            x="Kurztext",
            y="Erfasste Menge",
            title="Tage Faktura nach Projekt",
            labels={"Kurztext": "Projekt"},
            template="plotly_white",
        )
        bar_fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
        bar_fig.update_traces(texttemplate="%{y:.2f} PT", textposition="auto")

        return gauge_fig, bar_fig, bar_fig, config, config

    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value")
    )
    def update_interval_bar_chart(start_date, end_date, interval):
        # Für das Interval-Chart verwenden wir den kompletten DataFrame (alle Projekte)
        df = data_processing.df_all.copy()
        df_agg = data_processing.filter_and_aggregate_by_interval_stacked(df, start_date, end_date, interval)

        # Erstelle das gestackte Balkendiagramm
        fig = px.bar(
            df_agg,
            x="ProTime-Datum",
            y="Erfasste Menge",
            color="Kurztext",
            title=f"Stunden aggregiert nach {interval} und Projekt",
            labels={
                "ProTime-Datum": interval,
                "Erfasste Menge": "Stunden",
                "Kurztext": "Projekt"
            },
            template="plotly_white"
        )
        fig.update_layout(barmode="stack", paper_bgcolor="rgba(0,0,0,0)")
        fig.update_traces(texttemplate="%{y:.2f}", textposition="auto")
        return fig
