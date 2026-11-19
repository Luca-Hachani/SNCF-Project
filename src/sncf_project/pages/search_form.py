"""Trip search form page for planning TGV-to-airport connections.

Provides browser geolocation matching to automatically detect the closest
commune, renders an interactive trip criteria form, and resolves the nearest
TGV departure stations for the traveler.
"""

import datetime
import logging
import time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from sncf_project.models.traveler import Traveler
from sncf_project.models.trip_SNCF import Trip
from sncf_project.pages.render_trip_recommendations import render_trip_recommendations
from sncf_project.settings import (
    DATASET_COMMUNES_PATH,
    DATASET_RELIABLE_PATH,
    DATASET_STATIONS_PATH,
    STATION_TO_AIRPORT,
)
from sncf_project.utils import load_dataset

logger = logging.getLogger("sncf_project.pages.search_form")


def find_closest_commune(
    df_communes: pd.DataFrame, lat: float, lon: float
) -> str | None:
    """Return the closest commune name to a given ``(lat, lon)`` coordinate pair.

    Computes squared Euclidean distance in ``(latitude, longitude)`` space
    across all non-null communes in ``df_communes`` and returns the name of
    the nearest commune.

    Args:
        df_communes (pd.DataFrame): Communes DataFrame containing
            ``"nom_de_la_commune"``, ``"latitude"``, and ``"longitude"``
            columns.
        lat (float): Target latitude in decimal degrees.
        lon (float): Target longitude in decimal degrees.

    Returns:
        str | None: Name of the closest commune, or ``None`` if no valid
            commune coordinates exist.
    """
    valid_communes = df_communes.dropna(
        subset=["nom_de_la_commune", "latitude", "longitude"]
    )
    if valid_communes.empty:
        return None

    lats = pd.to_numeric(valid_communes["latitude"], errors="coerce").to_numpy()
    lons = pd.to_numeric(valid_communes["longitude"], errors="coerce").to_numpy()
    distances = (lats - lat) ** 2 + (lons - lon) ** 2
    closest_idx = int(np.nanargmin(distances))
    return str(valid_communes.iloc[closest_idx]["nom_de_la_commune"])


def render_airport_form(df_communes: pd.DataFrame) -> Traveler | None:
    """Render the trip search form with optional browser geolocation auto-fill.

    Displays a geolocation button that maps the visitor's GPS coordinates to the
    nearest French commune and pre-selects it in the city dropdown. Renders the
    airport, travel date, and departure city inputs inside a Streamlit form and
    returns a ``Traveler`` instance upon valid submission.

    Args:
        df_communes (pd.DataFrame): Communes DataFrame containing
            ``"nom_de_la_commune"``, ``"latitude"``, and ``"longitude"``.

    Returns:
        Traveler | None: A populated ``Traveler`` object when the form is
            submitted with all required fields, or ``None`` otherwise.
    """

    PARIS_TZ = ZoneInfo("Europe/Paris")
    today = datetime.datetime.now(PARIS_TZ).date()
    communes = df_communes["nom_de_la_commune"].dropna().unique().tolist()

    geo_col1, geo_col2 = st.columns([1, 6])
    with geo_col1:
        location = streamlit_geolocation()
    with geo_col2:
        st.caption(
            "📍 Click the location icon to automatically detect your departure city."
        )

    if (
        location
        and location.get("latitude") is not None
        and location.get("longitude") is not None
    ):
        coords = (location["latitude"], location["longitude"])
        if st.session_state.get("last_geo_coords") != coords:
            nearest_city = find_closest_commune(
                df_communes,
                lat=float(location["latitude"]),
                lon=float(location["longitude"]),
            )
            if nearest_city and nearest_city in communes:
                st.session_state["departure_city_select"] = nearest_city
                st.session_state["last_geo_coords"] = coords
                logger.info("Geolocation matched nearest commune: %s", nearest_city)

    with st.form("airport_form", border=True):
        st.subheader("Schedule your perfect train ticket!")

        airport_options = sorted(set(STATION_TO_AIRPORT.values()))
        departure_airport = st.selectbox(
            "Airport Departure",
            options=airport_options,
            index=None,
            placeholder="Write down the airport name",
        )

        col_date, col_train_station = st.columns([2, 3])

        with col_date:
            trip_date = st.date_input(
                "Day of the flight",
                value=today,
                format="DD/MM/YYYY",
            )

        communes = df_communes["nom_de_la_commune"].dropna().unique().tolist()
        with col_train_station:
            departure_city = st.selectbox(
                "From which city do you want to go ?",
                options=communes,
                index=None,
                key="departure_city_select",
                placeholder="Write down the city... (Upper Case)",
            )

        submitted = st.form_submit_button(
            "Estimate your delay",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not all([departure_airport, trip_date, departure_city]):
            st.warning("Please fill all the form!")
            return None

        logger.info(
            f"User submitted a request with theses values \n \
                    departure aiport : {departure_airport}\n \
                    date : {trip_date} \n \
                    departure city : {departure_city}"
        )
        return Traveler(departure_airport, trip_date, departure_city)

    return None


def main() -> None:
    """Load datasets, render the trip search form, and compute departure stations."""
    df_communes = load_dataset(DATASET_COMMUNES_PATH, sep=",")
    df_reg = load_dataset(DATASET_RELIABLE_PATH, sep=",")
    df_stations = load_dataset(DATASET_STATIONS_PATH)

    if df_communes is None or df_reg is None or df_stations is None:
        logger.error(
            "Datasets failed to load: df_communes=%s, df_reg=%s, df_stations=%s",
            df_communes is not None,
            df_reg is not None,
            df_stations is not None,
        )
        st.error(
            "Unable to load SNCF datasets. Check logs/error.log for the exact file path error."
        )
        st.stop()

    with st.container():
        traveler = render_airport_form(df_communes)

    if traveler:
        try:
            traveler.compute_departure_station(df_reg, df_stations, df_communes)
        except ValueError as exc:
            logger.warning("Station lookup failed for %s", exc)
            st.warning(str(exc))
            st.stop()

        logger.info("Traveler info %s", traveler)

        with st.spinner("Finding your best rides..."):
            Trip.load_datasets()
            time.sleep(1)
            routes: list[tuple[list[str], float]] = []
            for idx, departure_station in range(traveler.get_departure_station):
                trip = Trip(
                    _departure_station=traveler.get_departure_station[idx],
                    _trip_date=traveler.get_trip_date,
                    _arrival_airport=traveler.get_departure_airport,
                )
                trip.set_shortest_path()
                trip.set_arrival_station()
                trip.set_trip_reliability()
                logger.info(
                    f"shortest path: {trip.get_shortest_path} and reliability : {trip.get_trip_reliability}"
                )
                if trip.get_shortest_path and trip.get_trip_reliability is not None:
                    routes.append(
                        (trip.get_shortest_path, float(trip.get_trip_reliability))
                    )

            render_trip_recommendations(routes, traveler.get_departure_airport)


if __name__ == "__main__":
    main()
