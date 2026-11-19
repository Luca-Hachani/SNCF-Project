"""Tests for the Traveler domain model (src/sncf_project/models/traveler.py)."""

import datetime

import pandas as pd
import pytest

from sncf_project.models.traveler import Traveler


@pytest.fixture
def sample_datasets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create minimal regularity, stations, and communes DataFrames for testing."""
    df_reg = pd.DataFrame(
        {
            "Gare de départ": [
                "CAEN",
                "CAEN",  # Duplicate in df_reg to verify drop_duplicates
                "PARIS MONTPARNASSE",
                "RENNES",
                "MARSEILLE ST CHARLES",
                None,  # NaN entry to verify dropna handling
            ]
        }
    )
    df_stations = pd.DataFrame(
        {
            "LIBELLE": [
                "Caen",
                "Caen",  # Duplicate station coordinates to verify groupby mean
                "Paris-Montparnasse",
                "Rennes",
                "Marseille-St-Charles",
                "Bordeaux-St-Jean",  # Present in stations, absent from df_reg
            ],
            "X_WGS84": [-0.348, -0.350, 2.320, -1.672, 5.380, -0.556],
            "Y_WGS84": [49.176, 49.178, 48.841, 48.103, 43.303, 44.826],
        }
    )
    df_communes = pd.DataFrame(
        {
            "nom_de_la_commune": ["Caen", "Lyon"],
            "longitude": [-0.370, 4.835],
            "latitude": [49.182, 45.764],
        }
    )
    return df_reg, df_stations, df_communes


def test_traveler_initialization_and_getters() -> None:
    """Verify Traveler initialization and all property getters."""
    trip_date = datetime.date(2026, 7, 15)
    traveler = Traveler("CDG", trip_date, "Caen")

    assert traveler.get_departure_airport == "CDG"
    assert traveler.get_trip_date == trip_date
    assert traveler.get_departure_city == "Caen"
    assert traveler.get_departure_station is None


def test_compute_departure_station_finds_top_3_and_does_not_mutate_inputs(
    sample_datasets: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
) -> None:
    """Verify compute_departure_station finds the 3 closest unique stations cleanly."""
    df_reg, df_stations, df_communes = sample_datasets
    reg_cols_before = list(df_reg.columns)
    stations_cols_before = list(df_stations.columns)

    traveler = Traveler("LYS", datetime.date(2026, 7, 15), "Caen")
    traveler.compute_departure_station(df_reg, df_stations, df_communes)

    assert traveler.get_departure_station == [
        "Caen",
        "Rennes",
        "Paris-Montparnasse",
    ]
    assert list(df_reg.columns) == reg_cols_before
    assert list(df_stations.columns) == stations_cols_before


def test_compute_departure_station_unknown_city_raises_value_error(
    sample_datasets: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
) -> None:
    """Verify ValueError is raised when departure city is missing from df_communes."""
    df_reg, df_stations, df_communes = sample_datasets
    traveler = Traveler("LYS", datetime.date(2026, 7, 15), "UnknownCity")

    with pytest.raises(
        ValueError, match="Departure city not found in communes dataset"
    ):
        traveler.compute_departure_station(df_reg, df_stations, df_communes)
