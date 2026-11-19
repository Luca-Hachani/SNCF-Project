"""Data visualization page for the SNCF Project Streamlit application.

Loads the TGV monthly regularity and station coordinate datasets, provides an
interactive table preview, show the stations maps and display for a certain route the trends (delays and cancellation)
"""

import logging

import plotly.express as px
import streamlit as st

from sncf_project.config import (
    DATASET_RE_MEN_TGV_PATH,
    DATASET_STATIONS_PATH,
)
from sncf_project.pages.map_stations import render_map_stations
from sncf_project.pages.render_df_visualisation import render_df_visualisation
from sncf_project.utils import load_dataset

logger = logging.getLogger("sncf_project.pages.data_visualization")

df_reg = load_dataset(DATASET_RE_MEN_TGV_PATH)
df_stations = load_dataset(DATASET_STATIONS_PATH)

if df_reg is None or df_stations is None:
    logger.error(
        "Datasets failed to load: df_reg=%s, df_stations=%s",
        df_reg is not None,
        df_stations is not None,
    )
    st.error(
        "Unable to load SNCF datasets. Check logs/error.log for the exact file path error."
    )
    st.stop()

logger.info("Display Data Visualization")

st.title("📊 SNCF Data Visualization")
st.subheader("Explore the Dataset !")

st.subheader("Preview of some rows..")

st.divider()

render_df_visualisation(df_reg)

view_mode = st.radio(
    "Choose the rows..",
    ["First 10 rows", "Sample of 10 rows"],
    horizontal=True,
)

if view_mode == "First 10 rows":
    st.dataframe(df_reg.head(10), width="stretch")
else:
    if st.button("🔄 Resample"):
        st.rerun()
    st.dataframe(df_reg.sample(n=min(10, len(df_reg))), width="stretch")

st.divider()

df_cancelled_delays = df_reg.groupby("Date", as_index=False).agg(
    {
        "Nombre trains en retard > 15min": "sum",
        "Nombre trains en retard > 30min": "sum",
        "Nombre trains en retard > 60min": "sum",
        "Nombre de trains annulés": "sum",
    }
)

figure_metrics = px.bar(
    df_cancelled_delays,
    x="Date",
    y=[
        "Nombre trains en retard > 15min",
        "Nombre trains en retard > 30min",
        "Nombre trains en retard > 60min",
        "Nombre de trains annulés",
    ],
    title="Monthly cancelled / delayed trains",
    labels={"value": "Number of trains", "variable": "Category"},
    color_discrete_sequence=["#EFCF43", "#C96711", "#D02A17", "#253E56"],
)

st.plotly_chart(figure_metrics, width="content")

st.divider()

render_map_stations(df_reg, df_stations)

st.divider()
