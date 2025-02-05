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
        Input("interval-dropdown", "value"),
    )
    def update_hours_burndown(start_date, end_date, interval):
        # 1) Hol dir die täglichen Daten über deine vorhandene Funktion:
        df_fact = data_processing.df_faktura.copy()
        df_all = data_processing.df_all.copy()

        all_days, actual_cum, ideal_values, df_bar = data_processing.get_burndown_data(
            df_fact, df_all, start_date, end_date, target=160
        )

        # 2) Baue einen DataFrame für die Liniendaten (kumulative Ist & Ideal):
        df_lines = pd.DataFrame(
            {"Datum": all_days, "actual_cum": actual_cum.values, "ideal": ideal_values}
        )
        df_lines.set_index("Datum", inplace=True)

        # 3) Setze auch df_bar auf einen Datumsindex:
        df_bar.set_index("Datum", inplace=True)

        # 4) Falls dein interval in data_processing "ME" heißt, musst du eine
        #    Frequenz definieren, die pandas versteht.
        #    Typisch wäre "W" = wöchentlich (Sonntags als Periodenende),
        #    "M" = monatlich (Monatsende).
        #
        #    Wenn du explizit "ME" (Month End) nutzen willst, kannst du das
        #    Mapping so regeln:
        freq_map = {
            "D": None,  # daily => keine Resample-Änderung
            "W": "W",  # wöchentlicher Resample (Periodenende ist Sonntag)
            "ME": "ME",  # "Month End" in pandas = "ME"
        }
        freq = freq_map.get(interval, None)

        # 5) Wenn interval = D, dann bleiben wir daily.
        #    Wenn interval = W oder ME, machen wir ein Resampling => wir holen
        #    uns jeweils den letzten kumulativen Wert pro Periode (last).
        if freq is not None:
            # Liniendaten resamplen
            df_lines_resampled = df_lines.resample(freq).last().dropna(how="all")

            # Für die Balken:
            df_bar_resampled = df_bar.resample(freq).last().dropna(how="all")
        else:
            # daily
            df_lines_resampled = df_lines
            df_bar_resampled = df_bar

        # Um später erneut die x-Achse etc. zuzugreifen,
        # holen wir uns wieder eine "Datum"-Spalte:
        df_lines_resampled = df_lines_resampled.reset_index()
        df_bar_resampled = df_bar_resampled.reset_index()

        # 6) Erstelle die Plotly-Figur
        fig = go.Figure()

        # ============= A) Balken-Traces =============

        # Bei "D" (täglicher Anzeige) willst du wahrscheinlich weiterhin
        # mehrere Gruppen (Wochenende, Urlaub, Krank, Feiertag, Arbeitstag)
        # unterschiedlich einfärben.
        # Bei wöchentlicher / monatlicher Verdichtung macht
        # eine Tag-zu-Tag-Farbe oft weniger Sinn,
        # weil du jetzt nur 1 Balken pro Woche/Monat hast.
        # Du kannst deshalb bspw. bedingt den Code anpassen:

        if interval == "D":
            # Definierte Reihenfolge für die Legende:
            group_order = [
                "Wochenende",
                "Urlaub",
                "Krankheit",
                "Feiertag",
                "Arbeitstag",
            ]
            for grp in group_order:
                dfg = df_bar_resampled[df_bar_resampled["group"] == grp]
                if not dfg.empty:
                    fig.add_trace(
                        go.Bar(
                            x=dfg["Datum"],
                            y=dfg["Tatsächliche Faktura"],
                            name=grp,
                            marker_color=dfg["color"].iloc[0],
                            marker_opacity=dfg["opacity"].tolist(),
                            width=86400000 * 0.9,  # etwas schmaler als 1 Tag
                        )
                    )
        else:
            # z.B. nur *einen* Balkentrace (kumulative Faktura) ohne Tagtyp-Färbung
            fig.add_trace(
                go.Bar(
                    x=df_bar_resampled["Datum"],
                    y=df_bar_resampled["Tatsächliche Faktura"],
                    name="Kumulierte Faktura",
                    marker_color="#1f77b4",
                )
            )

        # ============= B) Linien-Traces (Ist & Ideal) =============
        # Du nutzt bisher nur die "Ideallinie". Falls du "Tatsächliche Faktura"
        # auch als Linie hättest, könntest du sie hier ebenfalls hinzufügen.
        # Aktuell reicht der "Ideallinie"-Trace:

        fig.add_trace(
            go.Scatter(
                x=df_lines_resampled["Datum"],
                y=df_lines_resampled["ideal"],
                mode="lines",
                name="Ideallinie",
                line=dict(color="red"),  # dash="dot" oder so
            )
        )

        # ============= Layout-Einstellungen =============
        fig.update_layout(
            title=f"Kumulative Faktura & Ideallinie",
            xaxis_title="",
            yaxis_title="Kumulative Faktura (PT)",
            template="plotly_white",
            height=500,
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
