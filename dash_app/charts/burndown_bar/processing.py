import plotly.graph_objects as go
import pandas as pd
from common import data


def create_hours_burndown_chart(
    df_fact, df_all, start_date, end_date, interval, faktura_target
):
    df_fact["ProTime-Datum"] = pd.to_datetime(df_fact["ProTime-Datum"], unit="ms")
    df_all["ProTime-Datum"] = pd.to_datetime(df_all["ProTime-Datum"], unit="ms")

    # 1) Bestimme den Geschäftsjahresbereich und verfügbare Arbeitstage im GJ
    fy_start, fy_end = data.get_fiscal_year_range()
    total_available_fy = data.get_available_days(df_all, fy_start, fy_end)
    if total_available_fy == 0:
        total_available_fy = 1

    # 2) Verfügbare Arbeitstage im gewählten Zeitraum
    subrange_available = data.get_available_days(df_all, start_date, end_date)

    # 3) Dynamische Ziel-Berechnung (PT)
    daily_rate = faktura_target / total_available_fy
    dynamic_target = daily_rate * subrange_available

    # 4) Burndown-Daten berechnen (täglich)
    all_days, actual_cum, ideal_values, df_bar = data.get_burndown_data(
        df_fact, df_all, start_date, end_date, target=dynamic_target
    )

    # 5) Resampling vorbereiten
    df_lines = pd.DataFrame(
        {"Datum": all_days, "actual_cum": actual_cum.values, "ideal": ideal_values}
    ).set_index("Datum")
    df_bar = df_bar.set_index("Datum")

    freq_map = {"D": None, "W": "W", "ME": "ME"}
    freq = freq_map.get(interval, None)

    if freq is not None:
        df_lines_res = df_lines.resample(freq).last().dropna(how="all")
        df_bar_res = df_bar.resample(freq).last().dropna(how="all")
    else:
        df_lines_res = df_lines
        df_bar_res = df_bar

    df_lines_res = df_lines_res.reset_index()
    df_bar_res = df_bar_res.reset_index()

    # 6) Figure erstellen
    fig = go.Figure()

    if interval == "D":
        group_order = ["Wochenende", "Urlaub", "Krankheit", "Feiertag", "Arbeitstag"]
        for grp in group_order:
            dfg = df_bar_res[df_bar_res["group"] == grp]
            if not dfg.empty:
                fig.add_trace(
                    go.Bar(
                        x=dfg["Datum"],
                        y=dfg["Tatsächliche Faktura"],
                        name=grp,
                        marker_color=dfg["color"].iloc[0],
                        marker_opacity=dfg["opacity"].tolist(),
                        width=86400000 * 0.9,  # ca. 1 Tag in ms
                    )
                )
    else:
        fig.add_trace(
            go.Bar(
                x=df_bar_res["Datum"],
                y=df_bar_res["Tatsächliche Faktura"],
                name="Kumulierte Faktura",
                text=df_bar_res["Tatsächliche Faktura"],
                marker_color="#1f77b4",
                opacity=0.9,
                textposition="inside",
                texttemplate="%{y:.2f} PT",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df_lines_res["Datum"],
            y=df_lines_res["ideal"],
            mode="lines",
            name="Ideallinie",
            line=dict(color="red"),
        )
    )
    fig.update_layout(
        title=f"Kumulative Faktura & Ideallinie ({interval})",
        xaxis_title="",
        yaxis_title="Kumulative Faktura (PT)",
        template=None,
        height=500,
        barmode="overlay",
        legend=dict(itemsizing="constant"),
    )
    fig.update_layout(paper_bgcolor="rgba(255,255,255,0)")

    return fig
