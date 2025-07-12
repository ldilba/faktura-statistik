import datetime
import plotly.graph_objects as go
import pandas as pd
import holidays
from common import data


def get_burndown_data(df_wertschoepfend, df_all, start_date, end_date, target=160):
    """
    Berechnet:
      - Die kumulative tatsächliche wertschöpfende Stunden (in PT) basierend auf df_wertschoepfend.
      - Eine dynamisch berechnete Ideallinie (in PT), unter Berücksichtigung von
        Feiertagen, Urlaub, Krankheit und Wochenenden.
      - Eine Prognoselinie basierend auf dem ersten und letzten gebuchten Eintrag.
      - Ein DataFrame (df_bar) mit zusätzlichen Informationen (Datum, Tagestyp,
        Farbe, Opacity, Gruppe) zur individuellen Formatierung der Balken im Chart.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Tatsächliche wertschöpfende Stunden berechnen (8 Stunden = 1 PT)
    mask_fact = (df_wertschoepfend["ProTime-Datum"] >= start_date) & (
        df_wertschoepfend["ProTime-Datum"] <= end_date
    )
    df_fact = df_wertschoepfend.loc[mask_fact].copy()
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
            "Tatsächliche Wertschöpfung": actual_cum.values,
            "day_type": day_types,
            "color": colors,
            "opacity": opacities,
            "group": groups,
        }
    )

    # Prognoselinie berechnen basierend auf tatsächlich gebuchten Daten
    forecast_values = []
    if not df_fact.empty:
        # Finde ersten und letzten tatsächlich gebuchten Tag aus den Originaldaten
        first_booked_date = df_fact["ProTime-Datum"].min()
        last_booked_date = df_fact["ProTime-Datum"].max()
        
        # Hole kumulative Werte zu diesen Zeitpunkten
        first_cum_value = actual_cum.loc[first_booked_date] if first_booked_date in actual_cum.index else 0
        last_cum_value = actual_cum.loc[last_booked_date] if last_booked_date in actual_cum.index else 0
        
        if first_booked_date != last_booked_date and last_cum_value > first_cum_value:
            # Berechne Steigung pro Tag basierend auf tatsächlichen Buchungen
            days_diff = (last_booked_date - first_booked_date).days
            daily_slope = (last_cum_value - first_cum_value) / days_diff
            
            # Erstelle Prognoselinie für alle Tage
            for day in all_days:
                days_from_first = (day - first_booked_date).days
                forecast_value = first_cum_value + (daily_slope * days_from_first)
                forecast_values.append(max(0, forecast_value))  # Keine negativen Werte
        else:
            forecast_values = [0] * len(all_days)
    else:
        forecast_values = [0] * len(all_days)

    return all_days, actual_cum, ideal_values, forecast_values, df_bar


def get_fiscal_year_range_for(any_date):
    """
    Liefert das Geschäftsjahr (01.04.–31.03.), das `any_date`
    enthält. akzeptiert str, Timestamp oder date.
    """
    d = pd.to_datetime(any_date).date()
    if d.month < 4:
        return (datetime.date(d.year - 1, 4, 1), datetime.date(d.year, 3, 31))
    else:
        return (datetime.date(d.year, 4, 1), datetime.date(d.year + 1, 3, 31))


def create_hours_burndown_chart(
    df_wertschoepfend, df_all, start_date, end_date, interval, wertschoepfend_target
):
    # ---------------------------------------------------------
    #  0) Vorbereitungen
    # ---------------------------------------------------------
    df_wertschoepfend["ProTime-Datum"] = pd.to_datetime(
        df_wertschoepfend["ProTime-Datum"], unit="ms"
    )
    df_all["ProTime-Datum"] = pd.to_datetime(df_all["ProTime-Datum"], unit="ms")

    # ---------------------------------------------------------
    #  1) Arbeitstage im Geschäftsjahr, das zum Auswahl-Intervall gehört
    # ---------------------------------------------------------
    fy_start, fy_end = get_fiscal_year_range_for(start_date)  # ❶
    total_available_fy = data.get_available_days(df_all, fy_start, fy_end)
    if total_available_fy == 0:
        total_available_fy = 1  # division-by-zero-safe

    # ---------------------------------------------------------
    #  2) Arbeitstage im ausgewählten Teil-Intervall
    # ---------------------------------------------------------
    subrange_available = data.get_available_days(df_all, start_date, end_date)

    # ---------------------------------------------------------
    #  3) Dynamische Ziel-PT
    # ---------------------------------------------------------
    daily_rate = wertschoepfend_target / total_available_fy
    dynamic_target = daily_rate * subrange_available

    # ---------------------------------------------------------
    #  4) Burndown-Daten (täglich)
    # ---------------------------------------------------------
    all_days, actual_cum, ideal_values, forecast_values, df_bar = get_burndown_data(
        df_wertschoepfend, df_all, start_date, end_date, target=dynamic_target
    )

    # ---------------------------------------------------------
    #  5) Resampling (D/W/Monat)
    # ---------------------------------------------------------
    df_lines = pd.DataFrame(
        {"Datum": all_days, "actual_cum": actual_cum.values, "ideal": ideal_values, "forecast": forecast_values}
    ).set_index("Datum")
    df_bar = df_bar.set_index("Datum")

    freq_map = {"D": None, "W": "W", "ME": "ME"}
    freq = freq_map.get(interval)

    if freq:
        df_lines_res = df_lines.resample(freq).last().dropna(how="all")
        df_bar_res = df_bar.resample(freq).last().dropna(how="all")
    else:
        df_lines_res = df_lines
        df_bar_res = df_bar

    df_lines_res = df_lines_res.reset_index()
    df_bar_res = df_bar_res.reset_index()

    # ---------------------------------------------------------
    #  6) Plot
    # ---------------------------------------------------------
    fig = go.Figure()

    if interval == "D":
        group_order = ["Wochenende", "Urlaub", "Krankheit", "Feiertag", "Arbeitstag"]
        for grp in group_order:
            dfg = df_bar_res[df_bar_res["group"] == grp]
            if not dfg.empty:
                fig.add_trace(
                    go.Bar(
                        x=dfg["Datum"],
                        y=dfg["Tatsächliche Wertschöpfung"],
                        name=grp,
                        marker_color=dfg["color"].iloc[0],
                        marker_opacity=dfg["opacity"].tolist(),
                        width=86400000 * 0.9,
                    )
                )
    else:
        fig.add_trace(
            go.Bar(
                x=df_bar_res["Datum"],
                y=df_bar_res["Tatsächliche Wertschöpfung"],
                name="Kumulierte Wertschöpfung",
                text=df_bar_res["Tatsächliche Wertschöpfung"],
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

    fig.add_trace(
        go.Scatter(
            x=df_lines_res["Datum"],
            y=df_lines_res["forecast"],
            mode="lines",
            name="Prognose",
            line=dict(color="grey", dash="dot"),
        )
    )

    fig.update_layout(
        title=f"Kumulative Wertschöpfung & Ideallinie ({interval})",
        xaxis_title="",
        yaxis_title="Kumulative Wertschöpfung (PT)",
        height=500,
        barmode="overlay",
        legend=dict(itemsizing="constant"),
        template=None,
        paper_bgcolor="rgba(255,255,255,0)",
    )

    return fig, {"displaylogo": False}
