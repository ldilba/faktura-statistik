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
            paper_bgcolor="rgba(255,255,255,0)",
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
            labels={"Kurztext": ""},
            template="plotly_white",
        )
        bar_fig.update_layout(height=400, paper_bgcolor="rgba(255,255,255,0)")
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
        # Nutzen Sie für die tatsächlichen Faktura-Daten ausschließlich df_faktura
        df_fact = data_processing.df_faktura.copy()
        # Für Abwesenheitsinformationen verwenden Sie df_all (enthält z. B. "Positionsbezeichnung")
        df_all = data_processing.df_all.copy()

        # Berechne alle benötigten Werte inkl. des Bar-DataFrames
        all_days, actual_cum, ideal_values, df_bar = data_processing.get_burndown_data(
            df_fact, df_all, start_date, end_date
        )

        # Erstelle den Figure-Container
        fig = go.Figure()

        # Definierte Reihenfolge der Gruppen für die Legende
        group_order = ["Wochenende", "Urlaub", "Krankheit", "Feiertag", "Arbeitstag"]

        # Für jede Gruppe einen eigenen Bar-Trace hinzufügen
        for grp in group_order:
            dfg = df_bar[df_bar["group"] == grp]
            if not dfg.empty:
                fig.add_trace(
                    go.Bar(
                        x=dfg["Datum"],
                        y=dfg["Tatsächliche Faktura"],
                        name=grp,
                        marker_color=dfg["color"].iloc[
                            0
                        ],  # alle Werte in der Gruppe haben dieselbe Farbe
                        marker_opacity=dfg[
                            "opacity"
                        ].tolist(),# individuelle Opacity pro Balken
                        width=86400000 * 0.9,
                        text=[f"{val:.2f} PT" for val in dfg["Tatsächliche Faktura"]],
                        textposition="auto",
                    )
                )

        # Ideallinie-Daten vorbereiten
        df_ideal = pd.DataFrame({"Datum": all_days, "Ideallinie": ideal_values})

        # Füge den Linien-Trace für die Ideallinie hinzu (rot, gestrichelt, mit Markern)
        fig.add_trace(
            go.Scatter(
                x=df_ideal["Datum"],
                y=df_ideal["Ideallinie"],
                mode="lines",
                name="Ideallinie",
                line=dict(color="red"),
            )
        )

        # Layout anpassen; barmode "overlay" funktioniert, da pro Tag immer nur ein Trace existiert
        fig.update_layout(
            title="Kumulative Faktura & Ideallinie",
            xaxis_title="",
            yaxis_title="Kumulative Faktura (PT)",
            template="plotly_white",
            height=400,
            barmode="overlay",
        )

        fig.update_layout(paper_bgcolor="rgba(255,255,255,0)")

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
                "ProTime-Datum": "",
                "Erfasste Menge": "Stunden",
                "Kurztext": "Projekt",
            },
            height=400,
            template="plotly_white",
        )
        fig.update_layout(barmode="stack", paper_bgcolor="rgba(255,255,255,0)")
        fig.update_traces(texttemplate="%{y:.2f}", textposition="auto")
        return fig
