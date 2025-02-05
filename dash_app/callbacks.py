import datetime

from dash import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import data_processing
import pandas as pd

YEAR_TARGET_PT = 160.0


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
            # height=225,
            margin=dict(t=25, l=50, r=50, b=0),
        )
        config = {"staticPlot": True}
        return gauge_fig, config

    @app.callback(
        Output("faktura-daily-avg-pt-content", "figure"),
        Output("faktura-daily-avg-pt-content", "config"),
        Output("faktura-daily-avg-hours-content", "figure"),
        Output("faktura-daily-avg-hours-content", "config"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_faktura_daily_needed(start_date, end_date):
        # 1) Summe der bisher geleisteten Faktura ermitteln
        df_faktura = data_processing.df_faktura.copy()
        df_grouped = data_processing.filter_data_by_date(
            df_faktura, start_date, end_date
        )
        faktura_sum = df_grouped["Erfasste Menge"].sum()

        # 2) Wie viele PT fehlen noch, um auf das Jahresziel (z.B. 160) zu kommen?
        remaining_pt = YEAR_TARGET_PT - faktura_sum
        if remaining_pt < 0:
            remaining_pt = 0  # Falls schon über 160

        # 3) Berechne die noch verfügbaren Arbeitstage
        df_all = data_processing.df_all.copy()
        today = datetime.date.today()
        end_date_date = pd.to_datetime(end_date).date()

        if end_date_date < today:
            remaining_days = 0
        else:
            remaining_days = data_processing.get_available_days(
                df_all, start_date=today, end_date=end_date_date
            )

        if remaining_days > 0:
            daily_needed_pt = remaining_pt / remaining_days
        else:
            daily_needed_pt = 0

        # Figure 1: PT pro Tag
        fig_pt = go.Figure()
        fig_pt.add_trace(
            go.Indicator(
                mode="number",
                value=daily_needed_pt,
                title={"text": "Ø PT pro Tag (Rest)", "font": {"size": 18}},
                number={"font": {"size": 35}},
            )
        )
        fig_pt.update_layout(
            height=100,
            paper_bgcolor="rgba(255,255,255,0)",
            margin=dict(t=75, l=50, r=50, b=50)
        )

        # Figure 2: Stunden pro Tag
        fig_hours = go.Figure()
        fig_hours.add_trace(
            go.Indicator(
                mode="number",
                value=daily_needed_pt * 8,
                title={"text": "Ø Stunden pro Tag (Rest)", "font": {"size": 18}},
                number={"font": {"size": 35}},
            )
        )
        fig_hours.update_layout(
            height=100,
            paper_bgcolor="rgba(255,255,255,0)",
            margin=dict(t=75, l=50, r=50, b=50)
        )

        config = {"staticPlot": True}

        return fig_pt, config, fig_hours, config

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
        """
        Callback, der den kumulativen Burndown-Chart (Faktura vs. Ideallinie) zurückgibt,
        inklusive dynamischer Anpassung des Ziels (Ideallinie) je nach ausgewähltem Zeitbereich
        und optionaler Wochen-/Monatsaggregation.
        """

        # 1) Hole Faktura- und All-Daten
        df_fact = data_processing.df_faktura.copy()
        df_all = data_processing.df_all.copy()

        # 2) Gesamt-Verfügbarkeit im Geschäftsjahr ermitteln
        fy_start, fy_end = (
            data_processing.get_fiscal_year_range()
        )  # z.B. 2024-04-01 bis 2025-03-31
        total_available_fy = data_processing.get_available_days(
            df_all, fy_start, fy_end
        )
        if total_available_fy == 0:
            total_available_fy = 1  # Edge Case vermeiden

        # 3) Verfügbare Tage im ausgewählten Bereich
        subrange_available = data_processing.get_available_days(
            df_all, start_date, end_date
        )

        # 4) Dynamische Ziel-Berechnung (PT)
        #    daily_rate = YEAR_TARGET_PT / verfügbare GJ-Tage => multipliziert mit verfügbaren Tagen im Sub-Bereich
        daily_rate = YEAR_TARGET_PT / total_available_fy
        dynamic_target = daily_rate * subrange_available

        # 5) Burndown-Daten (täglich) mit dynamischem Ziel berechnen
        all_days, actual_cum, ideal_values, df_bar = data_processing.get_burndown_data(
            df_fact, df_all, start_date, end_date, target=dynamic_target
        )

        # 6) DataFrames für (optionales) Resampling vorbereiten
        df_lines = pd.DataFrame(
            {"Datum": all_days, "actual_cum": actual_cum.values, "ideal": ideal_values}
        ).set_index("Datum")

        df_bar = df_bar.set_index("Datum")

        # Frequenzen mappen (pandas-Resample-String)
        freq_map = {
            "D": None,  # daily
            "W": "W",  # weekly
            "ME": "M",  # monthly (Month End)
        }
        freq = freq_map.get(interval, None)

        # 7) Falls W oder ME gewählt, resample auf "letzten" Tageswert je Periode
        if freq is not None:
            df_lines_res = df_lines.resample(freq).last().dropna(how="all")
            df_bar_res = df_bar.resample(freq).last().dropna(how="all")
        else:
            df_lines_res = df_lines
            df_bar_res = df_bar

        # Zurück in Spaltenform (für Plotly):
        df_lines_res = df_lines_res.reset_index()
        df_bar_res = df_bar_res.reset_index()

        # 8) Plotly-Figure erstellen
        fig = go.Figure()

        # a) Balken-Traces
        if interval == "D":
            # --- Tägliche Ansicht: verschiedene Farben je nach day_type ---
            group_order = [
                "Wochenende",
                "Urlaub",
                "Krankheit",
                "Feiertag",
                "Arbeitstag",
            ]
            for grp in group_order:
                dfg = df_bar_res[df_bar_res["group"] == grp]
                if not dfg.empty:
                    fig.add_trace(
                        go.Bar(
                            x=dfg["Datum"],
                            y=dfg["Tatsächliche Faktura"],
                            name=grp,
                            marker_color=dfg["color"].iloc[
                                0
                            ],  # alle in grp identische Farbe
                            marker_opacity=dfg[
                                "opacity"
                            ].tolist(),  # jede Zeile eigene Opacity
                            width=86400000
                            * 0.9,  # 1 Tag = 86400000 ms => balken etwas schmaler
                        )
                    )
        else:
            # --- Wöchentliche/Monatliche Ansicht: 1 Balken-Trace (nur kumulative Faktura) ---
            fig.add_trace(
                go.Bar(
                    x=df_bar_res["Datum"],
                    y=df_bar_res["Tatsächliche Faktura"],
                    name="Kumulierte Faktura",
                    marker_color="#1f77b4",
                    opacity=0.9,
                )
            )

        # b) Ideallinie-Trace
        fig.add_trace(
            go.Scatter(
                x=df_lines_res["Datum"],
                y=df_lines_res["ideal"],
                mode="lines",
                name="Ideallinie",
                line=dict(color="red"),  # gestrichelt, z.B.
            )
        )

        # c) Layout
        fig.update_layout(
            title=f"Kumulative Faktura & Ideallinie ({interval})",
            xaxis_title="",
            yaxis_title="Kumulative Faktura (PT)",
            template="plotly_white",
            height=500,
            barmode="overlay",  # Balken übereinander (nicht gestapelt)
            legend=dict(itemsizing="constant"),
        )
        # Hintergrund ggf. transparent
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
