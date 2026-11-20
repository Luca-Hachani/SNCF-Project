"""Interactive PyDeck map visualization for SNCF TGV stations."""

import logging

import pandas as pd
import pydeck as pdk
import streamlit as st

logger = logging.getLogger("sncf_project.pages.components.map_stations")


def render_map_stations(df_reg: pd.DataFrame, df_stations) -> None:
    """Render an interactive PyDeck map of unique TGV departure stations.

    Matches normalized station names from ``df_reg["Gare de départ"]`` against
    ``df_stations["LIBELLE"]``, averages coordinates for stations with multiple
    entries, and displays a ``ScatterplotLayer`` and ``TextLayer`` centered on
    France. Displays a Streamlit error message if expected columns are missing.

    Args:
        df_reg (pd.DataFrame): TGV monthly regularity DataFrame containing a
            ``"Gare de départ"`` column.
        df_stations (pd.DataFrame): Reference stations DataFrame containing
            ``"LIBELLE"``, ``"X_WGS84"`` (longitude), and ``"Y_WGS84"``
            (latitude) columns.

    Returns:
        None
    """
    if "Gare de départ" in df_reg.columns and "LIBELLE" in df_stations.columns:
        # Column gare_depart is uppercase and libelle is lowercase
        # In df_reg -> LYON PERRACHE
        # In df_stations -> Lyon-Perrache
        clean_reg_stations = (
            df_reg["Gare de départ"].dropna().str.upper().str.strip().unique()
        )

        """ rename column X_WGS84/Y_WGS84 into lon/lat to match
        colmuns name to match requirement to st.map"""
        clean_stations = pd.DataFrame(
            {
                "clean_station": (
                    df_stations["LIBELLE"]
                    .str.upper()
                    .str.strip()
                    .str.replace("-", " ", regex=False)
                ),
                "display_name": df_stations["LIBELLE"]
                .astype(str)
                .str.title()
                .str.strip(),
                "lon": pd.to_numeric(df_stations["X_WGS84"], errors="coerce"),
                "lat": pd.to_numeric(df_stations["Y_WGS84"], errors="coerce"),
            }
        )

        df_unique_pos = (
            clean_stations[
                clean_stations["clean_station"].isin(clean_reg_stations)
            ]
            .dropna(subset=["lon", "lat", "display_name"])
            .groupby("display_name", as_index=False)
            .agg({"lon": "mean", "lat": "mean"})
        )

        st.subheader("Map of all TGV SNCF stations in France")
        st.write(f"There are {len(df_unique_pos)} stations in the dataset")

        # Define the view state
        view_state = pdk.ViewState(
            latitude=47.92653148148473,  # Center of France latitude - Orléans
            longitude=1.9061071443118591,
            zoom=5,
            pitch=0,
        )

        # Define the layer
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_unique_pos,
            get_position="[lon, lat]",
            get_color="[255, 75, 75, 200]",
            get_radius=5000,
            pickable=True,
            stroked=True,  # Enable borders around dots
            get_line_color=[
                255,
                255,
                255,
                255,
            ],
            get_line_width=400,
            radius_min_pixels=4,
            radius_max_pixels=15,
            auto_highlight=True,
        )

        text_layer = pdk.Layer(
            "TextLayer",
            data=df_unique_pos,
            get_position="[lon, lat]",
            get_text="display_name",
            get_size=14,
            get_color="[201, 17, 63, 1]",
            get_alignment_baseline="'bottom'",
            get_pixel_offset="[0, 10]",
        )

        # Define the map_deck
        map_deck = pdk.Deck(
            layers=[scatter_layer, text_layer],
            initial_view_state=view_state,
            tooltip={
                "text": "Station: {display_name}\nLat: {lat}\nLon: {lon}"
            },
        )

        # Display the map
        st.pydeck_chart(map_deck)

    else:
        st.error("Expected columns gare de départ et libelle not found")
