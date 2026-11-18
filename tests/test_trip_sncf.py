import pytest
import pandas as pd
from unittest.mock import patch
# from trip_SNCF import Trip
from sncf_project.models.trip_SNCF import Trip
import sncf_project.settings as settings

@pytest.fixture(autouse=True)
def reset_trip_class_attributes():
    """Réinitialise les attributs de classe avant et après chaque test."""
    Trip._Trip__df_rail_links = None
    yield
    Trip._Trip__df_rail_links = None


# Test init and Getters in a row

def test_trip_initialization_and_getters():
    """Vérifie l'initialisation de l'objet Trip et le bon fonctionnement des getters de base."""
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST"
        )
    assert trip.get_departure_station == "MARSEILLE-STATION-TEST"
    assert trip.get_trip_date == "1789-07-14"
    assert trip.get_arrival_airport == "PARIS-AIRPORT-TEST"
    assert trip.get_arrival_station is None
    assert trip.get_shortest_path is None


# Test load_datasets()

def test_load_datasets():
    """
    Vérifie le chargement du dataset des liaisons ferroviaires via load_datasets.
    """
    mock_df = pd.DataFrame({
        "Gare de départ": ["MARSEILLE-STATION-TEST"],
        "Gare d'arrivée": ["PARIS-STATION-TEST"],
        "Durée moyenne du trajet": [180]
        })
    
    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.return_value = mock_df
        Trip.load_datasets()
        mock_read_csv.assert_called_once()
        assert Trip._Trip__df_rail_links is not None


# Test get_possible_arrival_stations()

def test_get_possible_arrival_stations():
    """
    Vérifie la récupération des gares d'arrivée associées à un aéroport cible.
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST"
        )
    with patch.dict(settings.STATION_TO_AIRPORT, {"PARIS-STATION-TEST": "PARIS-AIRPORT-TEST"}, clear=True):
        stations = trip.get_possible_arrival_stations()
        assert stations == ["PARIS-STATION-TEST"]


# Test get_path_to_target_station() (2 tests)

def test_get_path_to_target_station_not_loaded():
    """
    Vérifie qu'une exception ValueError est levée si le dataset n'est pas chargé.
    """
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST"
        )
    with pytest.raises(ValueError, match="Datasets must be loaded"):
        trip.get_path_to_target_station("PARIS-STATION-TEST")

def test_get_path_to_target_station_success_and_no_path():
    """
    Vérifie le calcul du chemin le plus court (succès) et la gestion d'un chemin inexistant.
    """
    df_links = pd.DataFrame({
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
            "BORDEAUX-STATION-TEST"
            ],
        "Durée moyenne du trajet": [
            90,
            90, 
            90,
            90,

            180,
            180,

            180,
            180
            ]
            })
    Trip._Trip__df_rail_links = df_links
    
    trip = Trip(
        _departure_station="MARSEILLE-STATION-TEST",
        _trip_date="1789-07-14",
        _arrival_airport="PARIS-AIRPORT-TEST"
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
    Vérifie la sélection du chemin le plus court en nombre de stops et la mise à jour de la gare d'arrivée.
    """
    # Path 1: "MARSEILLE-STATION-TEST" -> PARIS-STATION_1-TEST (1 rail link), 
    # Path 2: "MARSEILLE-STATION-TEST" -> PARIS-STATION_1-TEST -> PARIS-STATION_2-TEST  (2 rail links)
    df_links = pd.DataFrame({
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
        "Durée moyenne du trajet": [
            180, 
            180, 
            30,
            30]
            })
    Trip._Trip__df_rail_links = df_links
    
    with patch.dict(settings.STATION_TO_AIRPORT, 
                    {"PARIS-STATION_1-TEST": "PARIS-AIRPORT-TEST", 
                     "PARIS-STATION_2-TEST": "PARIS-AIRPORT-TEST"}, 
                     clear=True
                     ):
        trip = Trip(
            _departure_station="MARSEILLE-STATION-TEST",
            _trip_date="1789-07-14",
            _arrival_airport="PARIS-AIRPORT-TEST"
        )
        
        paths = trip.get_all_paths_to_possible_arrival_stations()
        assert len(paths) == 2
        
        # Test set_shortest_path (doit choisir le chemin direct le plus court en nombre de stations : ["MARSEILLE-STATION-TEST", "PARIS-STATION_1-TEST"])
        trip.set_shortest_path()
        assert trip.get_shortest_path == ["MARSEILLE-STATION-TEST", "PARIS-STATION_1-TEST"]
        
        # Test set_arrival_station
        trip.set_arrival_station()
        assert trip.get_arrival_station == "PARIS-STATION_1-TEST"

def test_set_shortest_path_no_paths_found():
    """
    Vérifie le comportement lorsque aucun chemin valide n'est trouvé.
    """
    Trip._Trip__df_rail_links = pd.DataFrame({
        "Gare de départ": ["MARSEILLE-STATION-TEST"],
        "Gare d'arrivée": ["LYON-STATION-TEST"],
        "Durée moyenne du trajet": [180]
    })
    with patch.dict(settings.STATION_TO_AIRPORT, {"PARIS-STATION-TEST": "PARIS-AIRPORT-TEST"}):
        trip = Trip(
            _departure_station="MARSEILLE-STATION-TEST",
            _trip_date="1789-07-14",
            _arrival_airport="PARIS-AIRPORT-TEST"
        )
        trip.set_shortest_path()
        assert trip.get_shortest_path is None
        
        trip.set_arrival_station()
        assert trip.get_arrival_station is None