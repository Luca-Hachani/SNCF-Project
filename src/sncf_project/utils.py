import logging

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger("utils")


@st.cache_data
def load_dataset(file_path: str, sep: str = ";") -> pd.DataFrame:
    """ "Load a CSV et return"""
    try:
        logger.info(f"Loading the dataset : {file_path}")
        df = pd.read_csv(file_path, sep=sep)
        logger.info(f"The {file_path} with {len(df)} row has been loaded")
        return df
    except FileNotFoundError:
        logger.error(f"File not found : {file_path}")
    except pd.errors.EmptyDataError:
        logger.error(f"The file at {file_path} is empty.")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse CSV structure in {file_path}: {e}")
        return None
    except PermissionError:
        logger.error(f"Permission denied while attempting to read: {file_path}")
        return None


def find_closest_stations(
    df_stations_pos: pd.DataFrame, lon_lat: list[int], top_n: int = 1
) -> list[str]:
    """Return the top_n closest stations from the geo position of the city"""

    required_cols = {"lon", "lat", "display_name"}
    missing_cols = required_cols - set(df_stations_pos.columns)

    if missing_cols:
        msg = f"Missing required columns in df_stations: {missing_cols}"
        raise ValueError(msg)

    if len(lon_lat) != 2 or any(pd.isna(coord) for coord in lon_lat):
        msg = f"Lon & Lat don't contain two valid coordinates: {lon_lat}"
        raise ValueError(msg)

    if top_n < 1:
        msg = f"Top_n must be > 1: {top_n}"
        raise ValueError(msg)

    if df_stations_pos.empty:
        return []

    lon_city, lat_city = lon_lat[0], lon_lat[1]
    lon_stations = df_stations_pos["lon"].to_numpy(dtype=float)
    lat_stations = df_stations_pos["lat"].to_numpy(dtype=float)

    distance = (lon_stations - lon_city) ** 2 + (lat_stations - lat_city) ** 2

    top_indices = np.argsort(distance)[:top_n]

    return df_stations_pos.iloc[top_indices]["display_name"].astype(str).tolist()
