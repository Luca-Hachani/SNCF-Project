import logging

import streamlit as st

from sncf_project.config import (
    DATASET_COMMUNES_PATH,
    DATASET_RE_MEN_TGV_PATH,
    DATASET_STATIONS_PATH,
)
from sncf_project.frontend.map_stations import render_map_stations
from sncf_project.frontend.search_form import render_airport_form
from sncf_project.utils import load_dataset

logger = logging.getLogger("streamlit_app")

st.set_page_config(
    page_title="Projet SNCF",
    page_icon="🚄",
    layout="wide",
)


def main():
    st.title("PROJET SNCF 🚄")

    logger.info("Streamlit application start")

    # Load the CSV File
    df_reg = load_dataset(DATASET_RE_MEN_TGV_PATH)
    df_stations = load_dataset(DATASET_STATIONS_PATH)
    df_communes = load_dataset(DATASET_COMMUNES_PATH, sep=",")

    if df_reg is not None and df_stations is not None:
        st.success("The datasets loaded successfully!")

        with st.container():
            render_airport_form(df_communes)

        with st.container():
            render_map_stations(df_reg, df_stations)

        with st.container():
            if st.checkbox("Preview des données"):
                st.dataframe(df_reg.head())
    else:
        st.error("Failed to load the datasets.. Check logs")
        logger.warning("The datasets did not load in the UI")


if __name__ == "__main__":
    main()
