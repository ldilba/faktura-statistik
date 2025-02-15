import plotly.graph_objects as go
import pandas as pd
import holidays
from common import data


def get_burndown_data(df_faktura, df_all, start_date, end_date, target=160):
    """
    Berechnet:
      - Die kumulative tatsächliche Faktura (in PT) basierend auf df_faktura.
      - Eine dynamisch berechnete Ideallinie (in PT), unter Berücksichtigung von
        Feiertagen, Urlaub, Krankheit und Wochenenden.
      - Ein DataFrame (df_bar) mit zusätzlichen Informationen (Datum, Tagestyp,
        Farbe, Opacity, Gruppe) zur individuellen Formatierung der Balken im Chart.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Tatsächliche Faktura berechnen (8 Stunden = 1 PT)
    mask_fact = (df_faktura["ProTime-Datum"] >= start_date) & (
        df_faktura["ProTime-Datum"] <= end_date
    )
    df_fact = df_faktura.loc[mask_fact].copy()
    df_fact["Erfasste Menge"] = df_fact["Erfasste Menge"] / 8.0
    df_daily = df_fact.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))[
        "Erfasste Menge"
    ].sum()
    df_daily = df_daily.reindex(all_days, fill_value=0)
    actual_cum = df_daily.cumsum()

    # Abwesenheitstage (Urlaub und Krankheit)
    absent_urlaub = set()
    absent_krank = set()
    if "Positionsbezeichnung" in df_all.columns:
        vacation_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Urlaub")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_urlaub = set(vacation_rows["ProTime-Datum"].dt.normalize().dt.date)
        krank_rows = df_all.loc[
            (df_all["Positionsbezeichnung"] == "Krank")
            & (df_all["ProTime-Datum"] >= start_date)
            & (df_all["ProTime-Datum"] <= end_date)
        ]
        absent_krank = set(krank_rows["ProTime-Datum"].dt.normalize().dt.date)

    # Feiertage in NRW bestimmen
    years = list(range(start_date.year, end_date.year + 1))
    nrw_holidays = holidays.Germany(prov="NW", years=years)
    holiday_dates = set(nrw_holidays.keys())

    # Verfügbare Arbeitstage bestimmen
    available = []
    for day in all_days:
        day_date = day.date()
        if (
            (day.weekday() < 5)
            and (day_date not in holiday_dates)
            and (day_date not in absent_urlaub)
            and (day_date not in absent_krank)
        ):
            available.append(True)
        else:
            available.append(False)

    # Dynamische Ideallinie berechnen
    ideal_values = []
    cumulative = 0.0
    remaining_target = float(target)
    for i, day in enumerate(all_days):
        if available[i]:
            remaining_available = sum(available[i:])
            daily_increment = (
                remaining_target / remaining_available if remaining_available > 0 else 0
            )
            cumulative += daily_increment
            remaining_target -= daily_increment
        ideal_values.append(cumulative)

    # Zusätzliche Daten für den Bar-Plot (z. B. zur individuellen Formatierung)
    if not df_all.empty:
        last_fact_date = df_all["ProTime-Datum"].max().date()
    else:
        last_fact_date = None

    # Für jeden Tag werden Tagestyp, Farbe, Opacity und Gruppe bestimmt:
    day_types = []
    colors = []
    opacities = []
    groups = []
    for day in all_days:
        day_date = day.date()
        if day_date in holiday_dates:
            d_type = "Feiertag"
            col = "grey"
        elif day_date in absent_urlaub:
            d_type = "Urlaub"
            col = "orange"
        elif day_date in absent_krank:
            d_type = "Krankheit"
            col = "purple"
        elif day.weekday() >= 5:
            d_type = "Wochenende"
            col = "green"
        else:
            d_type = "normal"
            col = "#1f77b4"
        grp = "Arbeitstag" if d_type == "normal" else d_type
        opac = 1
        if d_type in ["Wochenende", "Feiertag", "Urlaub", "Krankheit"]:
            opac = 0.6
        if last_fact_date is not None and day_date > last_fact_date:
            opac = 0.4
        day_types.append(d_type)
        colors.append(col)
        opacities.append(opac)
        groups.append(grp)

    df_bar = pd.DataFrame(
        {
            "Datum": all_days,
            "Tatsächliche Faktura": actual_cum.values,
            "day_type": day_types,
            "color": colors,
            "opacity": opacities,
            "group": groups,
        }
    )

    return all_days, actual_cum, ideal_values, df_bar


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
    all_days, actual_cum, ideal_values, df_bar = get_burndown_data(
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

    config = {"displaylogo": False}

    return fig, config
