from dash import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import data_processing
import pandas as pd


def register_callbacks(app):
    """Registriert die einzelnen Graph-Callbacks für die Dash-App."""

    # -------------------------------------------------------------------------
    # Callback für den Gauge (Faktura Total)
    @app.callback(
        Output("faktura-total-content", "figure"),
        Output("faktura-total-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_faktura_total(start_date, end_date):
        # Arbeite mit dem Faktura-DataFrame
        df = data_processing.df_faktura.copy()
        df_grouped = data_processing.filter_data_by_date(df, start_date, end_date)

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
        gauge_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=225,
            margin=dict(t=25, l=50, r=50, b=0),
        )
        config = {"staticPlot": True}
        return gauge_fig, config

    # -------------------------------------------------------------------------
    # Callback für das projektbezogene Balkendiagramm (Faktura Projekte)
    @app.callback(
        Output("faktura-projekt-content", "figure"),
        Output("faktura-projekt-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_faktura_projekt(start_date, end_date):
        df = data_processing.df_faktura.copy()
        df_grouped = data_processing.filter_data_by_date(df, start_date, end_date)

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
        config = {"staticPlot": True}
        return bar_fig, config

    # -------------------------------------------------------------------------
    # Callback für das Stunden Burndownchart
    @app.callback(
        Output("hours-burndown-content", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_hours_burndown(start_date, end_date):
        # Nutzen Sie hier für die tatsächlichen Faktura-Daten ausschließlich df_faktura
        df_fact = data_processing.df_faktura.copy()
        # Für Abwesenheitsinformationen verwenden Sie df_all (enthält z. B. "Positionsbezeichnung")
        df_all = data_processing.df_all.copy()

        # Berechne alle benötigten Werte inkl. des Bar-DataFrames
        all_days, actual_cum, ideal_values, df_bar = data_processing.get_burndown_data(df_fact, df_all, start_date,
                                                                                       end_date)

        # Erstelle den Figure-Container
        fig = go.Figure()

        # Balken-Trace: tatsächliche Faktura mit individuellen Farben und Opacity
        fig.add_trace(go.Bar(
            x=df_bar["Datum"],
            y=df_bar["Tatsächliche Faktura"],
            marker_color=df_bar["color"],
            marker_opacity=df_bar["opacity"],
            name="Tatsächliche Faktura",
            text=[f"{val:.2f} PT" for val in df_bar["Tatsächliche Faktura"]],
            textposition="auto"
        ))

        # DataFrame für die Ideallinie
        df_ideal = pd.DataFrame({
            "Datum": all_days,
            "Ideallinie": ideal_values
        })

        # Linie-Trace: Ideallinie in Rot mit Markern an jedem Tag
        fig.add_trace(go.Scatter(
            x=df_ideal["Datum"],
            y=df_ideal["Ideallinie"],
            mode="lines+markers",
            name="Ideallinie",
            line=dict(color="red", dash="dash")
        ))

        # Layout-Anpassungen
        fig.update_layout(
            title="Kumulative Faktura & Ideallinie",
            xaxis_title="Datum",
            yaxis_title="Kumulative Faktura (PT)",
            template="plotly_white",
            height=400
        )

        return fig

    # -------------------------------------------------------------------------
    # Callback für das gestapelte Intervall-Balkendiagramm (alle Projekte)
    @app.callback(
        Output("interval-bar-chart", "figure"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("interval-dropdown", "value"),
    )
    def update_interval_bar_chart(start_date, end_date, interval):
        df = data_processing.df_all.copy()
        df_agg = data_processing.filter_and_aggregate_by_interval_stacked(
            df, start_date, end_date, interval
        )

        fig = px.bar(
            df_agg,
            x="ProTime-Datum",
            y="Erfasste Menge",
            color="Kurztext",
            title="Stunden Übersicht",
            labels={
                "ProTime-Datum": interval,
                "Erfasste Menge": "Stunden",
                "Kurztext": "Projekt",
            },
            template="plotly_white",
        )
        fig.update_layout(barmode="stack", paper_bgcolor="rgba(0,0,0,0)")
        fig.update_traces(texttemplate="%{y:.2f}", textposition="auto")
        return fig
