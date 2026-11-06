import logging

import pandas as pd
import pydeck as pdk
import streamlit as st

from sncf_project.config import DATASET_RE_MEN_TGV_PATH, DATASET_STATIONS_PATH
from sncf_project.utils import load_dataset

logger = logging.getLogger("streamlit_app")

st.title("PROJET SNCF 🚄")
logger.info("Streamlit application start")

# Load the CSV File
df_reg = load_dataset(DATASET_RE_MEN_TGV_PATH)
df_stations = load_dataset(DATASET_STATIONS_PATH)

if df_reg is not None and df_stations is not None:
    st.success("The datasets loaded successfully!")

    # Verify the datasets
    if "Gare de départ" in df_reg.columns and "LIBELLE" in df_stations.columns:
        # Column gare_depart is uppercase and libelle is lowercase
        # In df_reg -> LYON PERRACHE
        # In df_stations -> Lyon-Perrache
        df_reg["clean_station"] = df_reg["Gare de départ"].str.upper().str.strip()
        df_stations["clean_station"] = (
            df_stations["LIBELLE"]
            .str.upper()
            .str.strip()
            .str.replace("-", " ", regex=False)
        )

        # Display stations name
        df_stations["display_name"] = df_stations["LIBELLE"].str.title().str.strip()

        # rename column X_WGS84/Y_WGS84 into lon/lat to match colmuns name to match requirement to st.map
        df_coords = df_stations[
            ["clean_station", "display_name", "X_WGS84", "Y_WGS84"]
        ].rename(columns={"X_WGS84": "lon", "Y_WGS84": "lat"})

        # Merge inner on stations
        df_pos_stations = pd.merge(df_reg, df_coords, on="clean_station", how="inner")

        # Drop duplicates
        df_unique_pos = (
            df_pos_stations[["lon", "lat", "display_name"]].drop_duplicates().dropna()
        )

        st.subheader("Map of all TGV SNCF stations")
        st.write(f"There are {len(df_unique_pos)} stations in the dataset")

        # Define the view state
        view_state = pdk.ViewState(
            latitude=47.92653148148473,  # Center of France latitude - Orléans
            longitude=1.9061071443118591,  # Center of France longitude - Orléans
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
            tooltip={"text": "Station: {display_name}\nLat: {lat}\nLon: {lon}"},
        )

        # Display the map
        st.pydeck_chart(map_deck)

    else:
        st.error("Expected columns gare de départ et libelle not found")

    if st.checkbox("Preview des données"):
        st.dataframe(df_reg.head())
else:
    st.error("Failed to load the datasets.. Check logs")
    logger.warning("The datasets did not load in the UI")
