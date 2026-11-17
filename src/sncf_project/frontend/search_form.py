import datetime
import logging
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from sncf_project.config import FRENCH_AIRPORTS

logger = logging.getLogger("streamlit_app")


def render_airport_form(df_communes: pd.DataFrame) -> None:
    # User form to get his information about is next schedule flight

    PARIS_TZ = ZoneInfo("Europe/Paris")
    today = datetime.datetime.now(PARIS_TZ).date()

    city = "Orléans"

    with st.form("airport_form", border=True):
        st.subheader("Schedule your perfect train ticket!")

        airport = st.selectbox(
            "Airport Departure",
            options=list(FRENCH_AIRPORTS.keys()),
            format_func=lambda code: FRENCH_AIRPORTS[code]["name"],
            index=None,
            placeholder="Write down the airport name or IATA code (ex: CDG, LYS..)",
        )

        col_date, col_train_station = st.columns([2, 3])

        with col_date:
            flight_date = st.date_input(
                "Day of the flight",
                value=today,
                format="DD/MM/YYYY",
            )

        communes = df_communes["nom_de_la_commune"].dropna().unique().tolist()
        with col_train_station:
            departure_city = st.selectbox(
                "From where do you want to go ?",
                options=communes,
                index=None,
                placeholder=city,
            )
            location = streamlit_geolocation()
            st.caption(
                "Click in the icon to automatically select your closest train station"
            )
            logger.info(f"{location}, {departure_city}, {flight_date}")

        submitted = st.form_submit_button(
            "Estimate your delay",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        logger.info("User submitted a request")
        return {
            "airport": airport,
        }
        city = "Paris"

    return None
