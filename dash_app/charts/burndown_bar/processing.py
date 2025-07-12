from typing import Tuple, Dict, Any, List
import datetime

import plotly.graph_objects as go
import pandas as pd
import holidays

from common import data
from common.constants import HOURS_PER_PT


def get_burndown_data(
    df_wertschoepfend: pd.DataFrame,
    df_all: pd.DataFrame,
    start_date: str,
    end_date: str,
    target: float = 160,
    vacation_days_pt: int = 0,
) -> Tuple[pd.DatetimeIndex, pd.Series, List[float], List[float], pd.DataFrame]:
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
    df_fact["Erfasste Menge"] = df_fact["Erfasste Menge"] / HOURS_PER_PT
    df_daily = df_fact.groupby(pd.Grouper(key="ProTime-Datum", freq="D"))[
        "Erfasste Menge"
    ].sum()
    # Originale tägliche Werte ohne Auffüllung für Prognoselinie
    df_daily_original = df_daily.copy()
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
        is_workday = (
            (day.weekday() < 5)
            and (day_date not in holiday_dates)
            and (day_date not in absent_urlaub)
            and (day_date not in absent_krank)
        )
        available.append(is_workday)

    # Zusätzliche Urlaubstage am Ende abziehen (rückwärts durch die Tage)
    additional_vacation_days = 0
    for i in range(len(all_days) - 1, -1, -1):
        if available[i] and additional_vacation_days < vacation_days_pt:
            available[i] = False
            additional_vacation_days += 1

    # Dynamische Ideallinie berechnen
    ideal_values = []
    
    # Finde letzten gebuchten Tag für Flatline-Logik
    last_booked_date = None
    if not df_daily_original.empty:
        last_booked_date = df_daily_original.index.max()
    
    if vacation_days_pt == 0 or last_booked_date is None:
        # Ohne Urlaubstage oder keine Buchungen: normale dynamische Berechnung
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
    else:
        # Mit Urlaubstagen: Flatline nach letztem gebuchten Tag
        # Finde Urlaubsperiode-Ende (gleiche Logik wie bei Prognoselinie)
        vacation_end_date = last_booked_date
        remaining_vacation_days = vacation_days_pt
        holiday_dates = set()
        if vacation_days_pt > 0:
            years = list(range(last_booked_date.year, last_booked_date.year + 2))
            nrw_holidays = holidays.Germany(prov="NW", years=years)
            holiday_dates = set(nrw_holidays.keys())
            
            # Berechne Abwesenheiten
            absent_urlaub = set()
            absent_krank = set()
            if "Positionsbezeichnung" in df_all.columns:
                vacation_rows = df_all.loc[df_all["Positionsbezeichnung"] == "Urlaub"]
                absent_urlaub = set(vacation_rows["ProTime-Datum"].dt.normalize().dt.date)
                krank_rows = df_all.loc[df_all["Positionsbezeichnung"] == "Krank"]
                absent_krank = set(krank_rows["ProTime-Datum"].dt.normalize().dt.date)
        
            for day in all_days:
                if day > last_booked_date and remaining_vacation_days > 0:
                    original_available = (
                        (day.weekday() < 5)
                        and (day.date() not in holiday_dates)
                        and (day.date() not in absent_urlaub)
                        and (day.date() not in absent_krank)
                    )
                    if original_available:
                        vacation_end_date = day
                        remaining_vacation_days -= 1
        
        # Berechne Ideallinie mit drei Phasen
        cumulative = 0.0
        remaining_target = float(target)
        
        # Berechne ursprünglich verfügbare Arbeitstage (ohne vacation_days_pt Abzug)
        original_available = []
        for day in all_days:
            day_date = day.date()
            is_workday = (
                (day.weekday() < 5)
                and (day_date not in holiday_dates)
                and (day_date not in absent_urlaub)
                and (day_date not in absent_krank)
            )
            original_available.append(is_workday)
        
        # Berechne verfügbare Tage für Zielverteilung
        available_until_last = sum(1 for j, d in enumerate(all_days) if d <= last_booked_date and original_available[j])
        available_after_vacation = sum(1 for j, d in enumerate(all_days) if d > vacation_end_date and original_available[j])
        total_work_days = available_until_last + available_after_vacation
        
        if total_work_days > 0:
            daily_increment = target / total_work_days
        else:
            daily_increment = 0
        
        # Phase 1: Bis letzter gebuchter Tag
        for i, day in enumerate(all_days):
            if day <= last_booked_date:
                if original_available[i]:
                    cumulative += daily_increment
                    remaining_target -= daily_increment
                ideal_values.append(cumulative)
            elif day <= vacation_end_date:
                # Phase 2: Urlaubsperiode - Flatline
                ideal_values.append(cumulative)
            else:
                # Phase 3: Nach Urlaubsperiode
                if original_available[i]:
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

    # Prognoselinie berechnen basierend auf tatsächlich gebuchten Daten (ohne Auffüllung)
    forecast_values = []
    if not df_daily_original.empty:
        # Finde ersten und letzten tatsächlich gebuchten Tag aus den originalen Daten
        first_booked_date = df_daily_original.index.min()
        last_booked_date = df_daily_original.index.max()

        # Berechne kumulative Werte basierend auf originalen täglichen Werten
        df_daily_original_cum = df_daily_original.cumsum()
        first_cum_value = df_daily_original_cum.loc[first_booked_date]
        last_cum_value = df_daily_original_cum.loc[last_booked_date]

        if first_booked_date != last_booked_date and last_cum_value > first_cum_value:
            # Berechne Steigung pro Tag basierend auf tatsächlichen Buchungen
            days_diff = (last_booked_date - first_booked_date).days
            daily_slope = (last_cum_value - first_cum_value) / days_diff

            if vacation_days_pt == 0:
                # Fall 1: 0 Resturlaub - Linie vom ersten durch letzten Wert, dann mit gleicher Steigung bis Ende

                # Erstelle Prognoselinie für alle Tage
                for day in all_days:
                    if day <= last_booked_date:
                        # Bis zum letzten gebuchten Tag: gerade Linie durch echte Werte
                        days_from_first = (day - first_booked_date).days
                        forecast_value = first_cum_value + (
                            daily_slope * days_from_first
                        )
                    else:
                        # Nach dem letzten gebuchten Tag: mit gleicher Steigung weiter
                        days_from_last = (day - last_booked_date).days
                        forecast_value = last_cum_value + (daily_slope * days_from_last)
                    forecast_values.append(max(0, forecast_value))
            else:
                # Fall 2: Mit Resturlaub - Steigung -> Flatline für Urlaubstage -> Steigung weiter
                # Finde das Ende der Urlaubsperiode (vacation_days_pt Arbeitstage nach letztem gebuchten Tag)
                vacation_end_date = last_booked_date
                remaining_vacation_days = vacation_days_pt

                # Finde das Ende der Urlaubsperiode
                for i, day in enumerate(all_days):
                    if day > last_booked_date and remaining_vacation_days > 0:
                        # Nur Arbeitstage zählen (original available ohne vacation_days_pt Reduktion)
                        original_available = (
                            (day.weekday() < 5)
                            and (day.date() not in holiday_dates)
                            and (day.date() not in absent_urlaub)
                            and (day.date() not in absent_krank)
                        )
                        if original_available:
                            vacation_end_date = day
                            remaining_vacation_days -= 1

                # Erstelle Prognoselinie für alle Tage
                for day in all_days:
                    if day <= last_booked_date:
                        # Bis zum letzten gebuchten Tag: gerade Linie durch echte Werte
                        days_from_first = (day - first_booked_date).days
                        forecast_value = first_cum_value + (
                            daily_slope * days_from_first
                        )
                    elif day <= vacation_end_date:
                        # Während der Urlaubsperiode: konstant (Flatline)
                        forecast_value = last_cum_value
                    else:
                        # Nach der Urlaubsperiode: mit gleicher Steigung weiter
                        days_after_vacation = (day - vacation_end_date).days
                        forecast_value = last_cum_value + (
                            daily_slope * days_after_vacation
                        )
                    forecast_values.append(max(0, forecast_value))
        else:
            forecast_values = [0] * len(all_days)
    else:
        forecast_values = [0] * len(all_days)

    return all_days, actual_cum, ideal_values, forecast_values, df_bar


def get_fiscal_year_range_for(any_date: str) -> Tuple[datetime.date, datetime.date]:
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
    df_wertschoepfend: pd.DataFrame,
    df_all: pd.DataFrame,
    start_date: str,
    end_date: str,
    interval: str,
    wertschoepfend_target: float,
    vacation_days_pt: int = 0,
) -> Tuple[go.Figure, Dict[str, Any]]:
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
    total_available_fy = data.get_available_days(
        df_all, fy_start, fy_end, vacation_days_pt
    )
    if total_available_fy == 0:
        total_available_fy = 1  # division-by-zero-safe

    # ---------------------------------------------------------
    #  2) Arbeitstage im ausgewählten Teil-Intervall
    # ---------------------------------------------------------
    subrange_available = data.get_available_days(
        df_all, start_date, end_date, vacation_days_pt
    )

    # ---------------------------------------------------------
    #  3) Dynamische Ziel-PT
    # ---------------------------------------------------------
    daily_rate = wertschoepfend_target / total_available_fy
    dynamic_target = daily_rate * subrange_available

    # ---------------------------------------------------------
    #  4) Burndown-Daten (täglich)
    # ---------------------------------------------------------
    all_days, actual_cum, ideal_values, forecast_values, df_bar = get_burndown_data(
        df_wertschoepfend,
        df_all,
        start_date,
        end_date,
        target=dynamic_target,
        vacation_days_pt=vacation_days_pt,
    )

    # ---------------------------------------------------------
    #  5) Resampling (D/W/Monat)
    # ---------------------------------------------------------
    df_lines = pd.DataFrame(
        {
            "Datum": all_days,
            "actual_cum": actual_cum.values,
            "ideal": ideal_values,
            "forecast": forecast_values,
        }
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
