"""Route-level reliability, delay trends, and root-cause analysis visualizations.

Provides interactive departure/arrival station selectors and a date range slider
to compute cancellation and delay metrics, monthly evolution bar charts, and
horizontal delay-cause breakdowns for a chosen TGV route.
"""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

logger = logging.getLogger("sncf_project.pages.render_df_visualisation")


def render_df_visualisation(df_reg: pd.DataFrame) -> None:
    """Render route selection controls, KPI metrics, and delay charts.

    Allows the user to filter ``df_reg`` by departure station, arrival station,
    and a ``YYYY-MM`` date period. Displays summary metrics for scheduled,
    cancelled, and delayed trains, followed by a monthly delay/cancellation bar
    chart and a horizontal bar chart of average delay causes.

    Args:
        df_reg (pd.DataFrame): TGV monthly regularity DataFrame containing route
            identifiers, train delay/cancellation counts, and delay cause
            percentage columns.

    Returns:
        None
    """
    st.subheader("Route Reliability & Delay Analysis")

    required_columns = {
        "Date",
        "Gare de départ",
        "Gare d'arrivée",
        "Nombre de circulations prévues",
        "Nombre trains en retard > 15min",
        "Nombre trains en retard > 30min",
        "Nombre trains en retard > 60min",
        "Nombre de trains annulés",
    }

    if not required_columns.issubset(df_reg.columns):
        logger.info(f"Missing some columns for analysis, df.columns: {df_reg.columns}")
        st.error("Missing some columns for analysis")
        return

    df_copy = df_reg.copy()
    df_copy["Date"] = df_copy["Date"].astype(str).str.strip()

    # Select a route
    col_departure, col_arrival = st.columns(2)
    with col_departure:
        departure_stations = sorted(df_copy["Gare de départ"].dropna().unique())
        selected_dep = st.selectbox(
            "Gare de Départ", departure_stations, key="route_departure_stations"
        )

    df_departure = df_copy[df_copy["Gare de départ"] == selected_dep]

    with col_arrival:
        arrival_stations = sorted(df_departure["Gare d'arrivée"].dropna().unique())
        selected_arr = st.selectbox(
            "Gare d'Arrivée", arrival_stations, key="route_arrival_stations"
        )

    df_route = df_departure[df_departure["Gare d'arrivée"] == selected_arr].sort_values(
        "Date"
    )

    if df_route.empty:
        logger.info(f"No route for theses 2 stations: {selected_dep}, {selected_arr}")
        st.warning("No route for theses 2 stations")
        return

    # Date selector
    available_dates = sorted(df_route["Date"].unique())
    if len(available_dates) >= 2:
        # Default range of 12 months
        default_start = available_dates[max(0, len(available_dates) - 12)]
        default_end = available_dates[-1]
        start_date, end_date = st.select_slider(
            "Select the period (Start : YYYY-MM & End : YYYY-MM)",
            options=available_dates,
            value=(default_start, default_end),
            key="route_date_stations",
        )

        df_date_route = df_route[df_route["Date"].between(start_date, end_date)]
    else:
        start_date = end_date = available_dates[0]
        df_date_route = df_route
        logger.info(f"There is no enough date range to show: {len(available_dates)}")
        st.warning("There is no date range data to show")

    if df_date_route.empty:
        logger.info("There is no data on the selected date range for this route")
        st.warning("There is no data on the selected date range for this route")
        return

    logger.info(
        f"Route selected {selected_dep} - {selected_arr}, {start_date} - {end_date}"
    )

    # Compute metrics
    total_scheduled = int(df_date_route["Nombre de circulations prévues"].sum())
    total_cancelled = int(df_date_route["Nombre de trains annulés"].sum())
    total_delay_15 = int(df_date_route["Nombre trains en retard > 15min"].sum())
    total_delay_30 = int(df_date_route["Nombre trains en retard > 30min"].sum())
    total_delay_60 = int(df_date_route["Nombre trains en retard > 60min"].sum())

    rate_cancelled = 0.0
    rate_delay_15 = 0.0
    rate_delay_30 = 0.0
    rate_delay_60 = 0.0

    if total_scheduled > 0:
        rate_cancelled = total_cancelled / total_scheduled * 100
        rate_delay_15 = total_delay_15 / total_scheduled * 100
        rate_delay_30 = total_delay_30 / total_scheduled * 100
        rate_delay_60 = total_delay_60 / total_scheduled * 100

    metrics1, metrics2, metrics3, metrics4, metrics5 = st.columns(5)
    metrics1.metric("Scheduled trains", f"{total_scheduled:,}")
    metrics2.metric(
        "Cancelled trains",
        f"{rate_cancelled:.1f}%",
    )
    metrics3.metric("Delay > 15 mins", f"{rate_delay_15:.1f}%")
    metrics4.metric("Delay > 30 mins", f"{rate_delay_30:.1f}%")
    metrics5.metric("Delay > 60 mins", f"{rate_delay_60:.1f}%")

    # Monthly evolution
    figure_metrics = px.bar(
        df_date_route,
        x="Date",
        y=[
            "Nombre trains en retard > 15min",
            "Nombre trains en retard > 30min",
            "Nombre trains en retard > 60min",
            "Nombre de trains annulés",
        ],
        title="Monthly canceled trains",
        labels={"value": "Number of trains", "variable": "Category"},
        color_discrete_sequence=["#EFCF43", "#C96711", "#D02A17", "#253E56"],
    )

    st.plotly_chart(figure_metrics, width="content")

    # Reasons of cancelled / Delayed
    causes_columns = [
        "Prct retard pour causes externes",
        "Prct retard pour cause infrastructure",
        "Prct retard pour cause gestion trafic",
        "Prct retard pour cause matériel roulant",
        "Prct retard pour cause gestion en gare et réutilisation de matériel",
        "Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances)",
    ]

    if not set(causes_columns).issubset(df_reg.columns):
        logger.info(
            f"Missing some columns for causes analysis, df.columns: {df_reg.columns}"
        )
        st.error("Missing some columns for causes analysis")
        return

    df_causes = df_date_route[causes_columns].mean().reset_index()
    df_causes.columns = ["Cause", "Pourcentage"]
    df_causes = df_causes.dropna().sort_values("Pourcentage", ascending=True)

    figure_causes = px.bar(
        df_causes,
        x="Pourcentage",
        y="Cause",
        orientation="h",
        title="Delay causes %",
        labels={"Pourcentage": "Percentage (%)", "Cause": ""},
        text_auto=".1f",
        color="Cause",
        color_discrete_sequence=[
            "#EFCF43",
            "#C96711",
            "#D02A17",
            "#253E56",
            "#2E86C1",
            "#16A085",
        ],
    )

    figure_causes.update_layout(showlegend=False)

    st.plotly_chart(figure_causes, width="content")
