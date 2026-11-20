from unittest.mock import patch

import pandas as pd
import pytest

import sncf_project.settings as settings

# from trip_SNCF import Trip
from sncf_project.models.trip_SNCF import Trip


@pytest.fixture(autouse=True)
def reset_trip_class_attributes():
    """
    Reset class attributes before and after each test.
    """
    Trip._Trip__df_rail_links = None
    yield
    Trip._Trip__df_rail_links = None


# Test init and Getters in a row


def test_trip_initialization_and_getters():
    """
    Verify Trip object initialization and proper behavior of basic
    getters.
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST",
    )
    assert trip.get_departure_station == "MARSEILLE-STATION-TEST"
    assert trip.get_trip_date == "1789-07-14"
    assert trip.get_arrival_airport == "PARIS-AIRPORT-TEST"
    assert trip.get_arrival_station is None
    assert trip.get_shortest_path is None
    assert trip.get_trip_reliability is None


# Test load_datasets()


def test_load_datasets():
    """
    Verify loading of the rail links dataset via load_datasets.
    """
    mock_df = pd.DataFrame(
        {
            "Gare de départ": ["MARSEILLE-STATION-TEST"],
            "Gare d'arrivée": ["PARIS-STATION-TEST"],
            "Durée moyenne du trajet": [180],
        }
    )

    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.return_value = mock_df
        Trip.load_datasets()
        mock_read_csv.assert_called_once()
        assert Trip._Trip__df_rail_links is not None


# Test get_possible_arrival_stations()


def test_get_possible_arrival_stations():
    """
    Verify retrieval of arrival train stations associated with a target
    airport.
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST",
    )
    with patch.dict(
        settings.STATION_TO_AIRPORT,
        {"PARIS-STATION-TEST": "PARIS-AIRPORT-TEST"},
        clear=True,
    ):
        stations = trip.get_possible_arrival_stations()
        assert stations == ["PARIS-STATION-TEST"]


# Test get_path_to_target_station() (2 tests)


def test_get_path_to_target_station_not_loaded():
    """
    Verify that a ValueError is raised when the dataset is not loaded.
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST",
    )
    with pytest.raises(ValueError, match="Datasets must be loaded"):
        trip.get_path_to_target_station("PARIS-STATION-TEST")


def test_get_path_to_target_station_success_and_no_path():
    """
    Verify shortest path calculation (success) and handling of an
    unreachable path.
    """
    df_links = pd.DataFrame(
        {
            "Gare de départ": [
                "MARSEILLE-STATION-TEST",
                "LYON-STATION-TEST",
                "LYON-STATION-TEST",
                "PARIS-STATION-TEST",
                "MARSEILLE-STATION-TEST",
                "PARIS-STATION-TEST",
                "BORDEAUX-STATION-TEST",
                "PARIS-STATION-TEST",
            ],
            "Gare d'arrivée": [
                "LYON-STATION-TEST",
                "MARSEILLE-STATION-TEST",
                "PARIS-STATION-TEST",
                "LYON-STATION-TEST",
                "PARIS-STATION-TEST",
                "MARSEILLE-STATION-TEST",
                "PARIS-STATION-TEST",
                "BORDEAUX-STATION-TEST",
            ],
            "Durée moyenne du trajet": [90, 90, 90, 90, 180, 180, 180, 180],
        }
    )
    Trip._Trip__df_rail_links = df_links

    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST",
    )

    # Path exist : MARSEILLE-STATION-TEST -> PARIS-STATION-TEST
    path = trip.get_path_to_target_station("PARIS-STATION-TEST")
    assert path == ["MARSEILLE-STATION-TEST", "PARIS-STATION-TEST"]

    # Station or path don't exist
    unreachable_path = trip.get_path_to_target_station("LILLE-STATION-TEST")
    assert unreachable_path == []


# Test get_all_paths_to_possible_arrival_stations


def test_get_all_paths_and_set_shortest_path_and_arrival():
    """
    Verify selection of the shortest path by number of stops and
    updating of the arrival station.
    """
    # Path 1: "MARSEILLE-STATION-TEST" -> PARIS-STATION_1-TEST (1 rail link),
    # Path 2: "MARSEILLE-STATION-TEST" -> PARIS-STATION_1-TEST
    #         -> PARIS-STATION_2-TEST  (2 rail links)
    df_links = pd.DataFrame(
        {
            "Gare de départ": [
                "MARSEILLE-STATION-TEST",
                "PARIS-STATION_1-TEST",
                "PARIS-STATION_1-TEST",
                "PARIS-STATION_2-TEST",
            ],
            "Gare d'arrivée": [
                "PARIS-STATION_1-TEST",
                "MARSEILLE-STATION-TEST",
                "PARIS-STATION_2-TEST",
                "PARIS-STATION_1-TEST",
            ],
            "Durée moyenne du trajet": [180, 180, 30, 30],
        }
    )
    Trip._Trip__df_rail_links = df_links

    with patch.dict(
        settings.STATION_TO_AIRPORT,
        {
            "PARIS-STATION_1-TEST": "PARIS-AIRPORT-TEST",
            "PARIS-STATION_2-TEST": "PARIS-AIRPORT-TEST",
        },
        clear=True,
    ):
        trip = Trip(
            _departure_station="MARSEILLE-STATION-TEST",
            _trip_date="1789-07-14",
            _arrival_airport="PARIS-AIRPORT-TEST",
        )

        paths = trip.get_all_paths_to_possible_arrival_stations()
        assert len(paths) == 2

        # Test set_shortest_path (doit choisir
        # le chemin direct le plus court en nombre de stations :
        # ["MARSEILLE-STATION-TEST", "PARIS-STATION_1-TEST"])
        trip.set_shortest_path()
        assert trip.get_shortest_path == [
            "MARSEILLE-STATION-TEST",
            "PARIS-STATION_1-TEST",
        ]

        # Test set_arrival_station
        trip.set_arrival_station()
        assert trip.get_arrival_station == "PARIS-STATION_1-TEST"


# Test set_shortest_path


def test_set_shortest_path_no_paths_found():
    """
    Verify behavior when no valid path is found.
    """
    df_links = pd.DataFrame(
        {
            "Gare de départ": ["MARSEILLE-STATION-TEST"],
            "Gare d'arrivée": ["LYON-STATION-TEST"],
            "Durée moyenne du trajet": [180],
        }
    )
    Trip._Trip__df_rail_links = df_links

    with patch.dict(
        settings.STATION_TO_AIRPORT,
        {"PARIS-STATION-TEST": "PARIS-AIRPORT-TEST"},
    ):
        trip = Trip(
            _departure_station="MARSEILLE-STATION-TEST",
            _trip_date="1789-07-14",
            _arrival_airport="PARIS-AIRPORT-TEST",
        )
        trip.set_shortest_path()
        assert trip.get_shortest_path is None

        trip.set_arrival_station()
        assert trip.get_arrival_station is None


# Test set_arrival_station & set_trip_reliability


def test_set_arrival_station_and_trip_reliability_wo_valid_shortest_path():
    """
    Verify that _trip_reliability is set to None
    when _shortest_path is None
    or contains fewer than two stations (no rail links).
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="MARSEILLE-AIRPORT-TEST",
    )

    # Case 1: _shortest_path is None
    trip._shortest_path = None
    trip.set_trip_reliability()
    assert trip.get_trip_reliability is None
    trip.set_arrival_station()
    assert trip.get_arrival_station is None

    # Case 2: _shortest_path has only one station (no rail links)
    trip._shortest_path = ["MARSEILLE-STATION-TEST"]
    trip.set_trip_reliability()
    assert trip.get_trip_reliability is None


def test_set_trip_reliability_success():
    """
    Verify that _trip_reliability equals the product of the reliabilities
    of the rail links along _shortest_path.
    """
    df_links = pd.DataFrame(
        {
            "Gare de départ": [
                "MARSEILLE-STATION-TEST",
                "LYON-STATION-TEST",
            ],
            "Gare d'arrivée": [
                "LYON-STATION-TEST",
                "PARIS-STATION-TEST",
            ],
            "Fiabilité": [0.5, 0.5],
        }
    )
    Trip._Trip__df_rail_links = df_links

    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST",
    )
    trip._shortest_path = [
        "MARSEILLE-STATION-TEST",
        "LYON-STATION-TEST",
        "PARIS-STATION-TEST",
    ]

    trip.set_trip_reliability()
    assert trip.get_trip_reliability == 0.25
