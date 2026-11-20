import logging

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger("sncf_project.utils")


@st.cache_data
def load_dataset(file_path: str, sep: str = ";") -> pd.DataFrame:
    """Load a CSV file into a cached pandas DataFrame.

    Reads the CSV file at ``file_path`` using ``sep`` as delimiter and caches
    the result via ``@st.cache_data``. Logs descriptive errors and returns
    ``None`` when the file is missing, empty, unreadable, or malformed.

    Args:
        file_path (str | Path): Path to the CSV file to load.
        sep (str, optional): Column delimiter character. Defaults to ``";"``.

    Returns:
        pd.DataFrame | None: Loaded DataFrame if successful, otherwise ``None``
    """
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
        logger.error(
            f"Permission denied while attempting to read: {file_path}"
        )
        return None


def find_closest_stations(
    df_stations_pos: pd.DataFrame, lon_lat: list[int], top_n: int = 1
) -> list[str]:
    """Return the ``top_n`` closest station names to a given
    ``[lon, lat]`` point.

    Computes squared Euclidean distance in ``(lon, lat)`` space between the
    target city coordinates and each station in ``df_stations_pos``, returning
    the nearest ``top_n`` station display names ordered from closest to
    farthest.

    Args:
        df_stations_pos (pd.DataFrame): DataFrame containing ``"lon"``,
            ``"lat"``, and ``"display_name"`` columns.
        lon_lat (Sequence[float]): Two-element sequence ``[lon, lat]``
            representing the target city's longitude and latitude.
        top_n (int, optional): Number of closest stations to return. Must be
            at least ``1``. Defaults to ``1``.

    Returns:
        list[str]: Ordered list of up to ``top_n`` closest station display
            names, or an empty list if ``df_stations_pos`` is empty.

    Raises:
        ValueError: If required columns are missing, ``lon_lat`` does not
            contain two non-null coordinates, or ``top_n < 1``.
    """

    required_cols = {"lon", "lat", "Gare de départ"}
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

    logger.info(df_stations_pos.iloc[top_indices].head(10))

    return (
        df_stations_pos.iloc[top_indices]["Gare de départ"]
        .astype(str)
        .tolist()
    )
