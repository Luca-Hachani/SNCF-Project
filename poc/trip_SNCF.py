from dataclasses import dataclass
# import logging
import numpy as np
import pandas as pd
import networkx as nx
from itertools import permutations
from settings import STATION_TO_AIRPORT

# logger = logging.getLogger(__name__)

@dataclass
class Trip:
    """
    Class representing a specific rail link,
    including departure, arrival, date, and associated punctuality metrics.

    Attributes
    ----------
    _departure_station : str
        The name of the departure train station.
    _trip_date : str
        The scheduled date of the trip (format: YYYY-MM-DD).
    _arrival_airport : str
        The associated airport at the arrival station, if a correspondence exists.
    _arrival_station : str, (set by set_arrival_station)
        The name of the arrival train station.
    _shortest_path : list, (set by set_shortest_path)
        The path with the fewest stations to the arrival train station.
    
    Class Attributes
    ----------------
    __df : pd.DataFrame
        Preprocessed main SNCF dataset loaded once at the class level.
    __df_airport_seasonality : pd.DataFrame
        Preprocessed aggregated seasonality metrics for airport-connected routes.
    __df_rail_links : pd.DataFrame
        Dataset containing all unique train route links (departure -> arrival).

    Methods
    -------
    load_datasets(df_path, seasonality_path, links_path) -> None
        Class method to load preprocessed CSV datasets into class-level attributes.
    get_departure_station() -> str
        Returns the departure train station.
    get_arrival_station() -> str
        Returns the arrival train station.
    get_trip_date() -> str
        Returns the scheduled date of the trip.
    get_arrival_airport() -> str
        Returns the associated arrival airport.
    get_shortest_path() -> list of str
        Returns the precomputed shortest path.
    get_possible_arrival_stations() -> list of str
        Lists all possible arrival train stations matching the target arrival airport.
    get_path_to_target_station(target_station: str) -> list of str
        Calculates the shortest path to a target station using the unique links graph.
    get_all_paths_to_stations() -> list of list of str
        Retrieves all valid shortest paths from the departure station to every target 
        station associated with the arrival airport.
    set_shortest_path() -> None
        Selects and assign the path with the fewest stations attribute 
        among all possible paths to the target airport.
    set_arrival_station() -> None
        Assigns the arrival station attribute using the last element 
        of the shortest path. 
        !!! The shortest path has to be computed !!!

    Notes
    -----
    - Acts as a core entity for evaluating train delays and connection risks.
    - Warning : we have to loading data before building any object such that for instance :
    with streamlit.spinner("Chargement des données SNCF en cours..."):
    Trip.load_datasets()

    Example
    -------
    #->1 : Load preprocessed datasets at startup :
    Trip.load_datasets()

    #->2 : Create a trip instance :
    trip = Trip(
        _departure_station="LYON PART DIEU",
        _arrival_station="PARIS LYON",
        _trip_date="2026-07-15",
        _arrival_airport="PARIS-ORLY / PARIS-CHARLES-DE-GAULLE"
    )
    #->3 : Get all stations matching the target airport :
    stations = trip.get_possible_arrival_stations()

    #->4 : Compute and set the shortest path by number of stops :
    trip.set_shortest_path()

    #->5 : Resolve and set the final arrival station attribute :
    #--------> The shortest path has been computed yet <--------
    trip.set_arrival_station()

    #->6 : Retrieve values using getters :
    selected_path = trip.get_shortest_path
    resolved_station = trip.get_arrival_station

    """
    _departure_station: str
    _trip_date: str
    _arrival_airport: str
    _arrival_station: str = None
    _shortest_path: list | None = None

    __df: pd.DataFrame = None
    __df_airport_seasonality: pd.DataFrame = None
    __df_rail_links: pd.DataFrame = None


    # Class method

    @classmethod
    def load_datasets(cls, 
                      df_path: str = "../data/processed_df.csv", 
                      seasonality_path: str = "../data/processed_airport_seasonality.csv", 
                      links_path: str = "../data/df_rail_links.csv") -> None:
        """
        Loads preprocessed datasets directly into class-level attributes.

        Parameters
        ----------
        df_path : str, optional
            Path to the main preprocessed SNCF dataset CSV.
        seasonality_path : str, optional
            Path to the preprocessed airport seasonality dataset CSV.
        links_path : str, optional
            Path to the unique links dataset CSV.

        Notes
        -----
        - Datasets are loaded only once at runtime to optimize memory and performance.
        """
        # logger.debug("Loading preprocessed datasets for Trip at class level")
        
        # if not hasattr(cls, "__df") or cls.__df is None:
        #     cls.__df = pd.read_csv(df_path)
            
        # if not hasattr(cls, "__df_airport_seasonality") or cls.__df_airport_seasonality is None:
        #     cls.__df_airport_seasonality = pd.read_csv(seasonality_path)
            
        if not hasattr(cls, "__df_rail_links") or cls.__df_rail_links is None:
            cls.__df_rail_links = pd.read_csv(links_path)


    # Getters

    @property
    def get_departure_station(self) -> str:
        """
        Returns the departure train station.

        Returns
        -------
        str
            The name of the departure station.
        """
        # logger.debug("Getting departure station for trip")
        return self._departure_station

    @property
    def get_arrival_station(self) -> str:
        """
        Returns the arrival train station.

        Returns
        -------
        str
            The name of the arrival station.
        """
        # logger.debug("Getting arrival station for trip")
        return self._arrival_station

    @property
    def get_trip_date(self) -> str:
        """
        Returns the scheduled date of the trip.

        Returns
        -------
        str
            The scheduled date (format: YYYY-MM-DD).
        """
        # logger.debug("Getting trip date")
        return self._trip_date

    @property
    def get_arrival_airport(self) -> str:
        """
        Returns the associated arrival airport.

        Returns
        -------
        str or None
            The associated airport name, or None if no correspondence exists.
        """
        # logger.debug("Getting arrival airport for trip")
        return self._arrival_airport

    @property
    def get_shortest_path(self) -> list[str]:
        """
        Returns the shortest path.

        Returns
        -------
        list of str
            The ordered list of stations representing the shortest path.
        """
        # logger.debug("Getting shortest path for trip")
        return self._shortest_path
    

    # Methods

    def get_possible_arrival_stations(self) -> list[str]:
        """
        Lists all possible arrival train stations associated with the traveler's 
        target arrival airport using the STATION_TO_AIRPORT mapping.

        Returns
        -------
        list of str
            A list of train station names that correspond to `_arrival_airport`.
        """
        # logger.debug(f"Listing possible arrival stations for airport: {self._arrival_airport}")

        # Extraction of train stations associated with the traveler's target arrival airport
        possible_arrival_stations = [
            station for station, airport in STATION_TO_AIRPORT.items() 
            if airport == self._arrival_airport
            ]
        
        return possible_arrival_stations

    def get_path_to_target_station(self, target_station: str) -> list[str]:
        """
        Computes the ordered list of stations to follow from the departure station 
        to a specific target station, minimizing the average travel time.

        Parameters
        ----------
        target_station : str
            The name of the target arrival station.

        Returns
        -------
        list of str
            The ordered list of stations representing the shortest path, 
            or an empty list if unreachable.
        """
        if Trip.__df_rail_links is None:
            # logger.error("Path computation attempt failed: the __df_rail_links dataset is not loaded.")
            raise ValueError("Datasets must be loaded via Trip.load_datasets() before computing a path.")

        # logger.debug(f"Computing the shortest path from '{self._departure_station}' to '{target_station}'")

        col_dep = "Gare de départ"
        col_arr = "Gare d'arrivée"
        col_weight = "Durée moyenne du trajet"

        G = nx.from_pandas_edgelist(
            Trip.__df_rail_links, 
            source=col_dep, 
            target=col_arr, 
            edge_attr=col_weight,
            create_using=nx.DiGraph()
        )

        try:
            # Compute the shortest path weighted by duration
            path = nx.shortest_path(
                G, 
                source=self._departure_station, 
                target=target_station, 
                weight=col_weight
            )
            # logger.debug(f"Path successfully found ({len(path)} stations traversed): {path}")
            return path
            
        except (nx.NodeNotFound, nx.NetworkXNoPath) as e:
            # logger.warning(f"Unable to connect '{self._departure_station}' to '{target_station}' (Exception: {type(e).__name__}).")
            print(f"Unable to connect '{self._departure_station}' to '{target_station}' (missing station or no path).")
            return []

    def get_all_paths_to_possible_arrival_stations(self) -> list[list[str]]:
        """
        Automatically retrieves the possible arrival stations associated with the target airport, 
        then computes and returns a list of all valid paths from the departure station 
        to each of those target stations.

        Returns
        -------
        list of list of str
            A list containing all valid paths found ([path_1, path_2, ...]).
        """
        possible_arrival_stations = self.get_possible_arrival_stations()
        
        # logger.debug(f"Computing paths from '{self._departure_station}' to {len(possible_arrival_stations)} target stations.")
        
        paths = []
        for target_station in possible_arrival_stations:
            path = self.get_path_to_target_station(target_station)
            if path:
                paths.append(path)
                
        return paths


    # Setters

    def set_shortest_path(self) -> None:
        """
        Retrieves the shortest path by number of stops (elements) among all possible 
        paths to the target airport.
        """
        paths = self.get_all_paths_to_possible_arrival_stations()
        
        if paths:
            # Extract the length of each path
            paths_lengths = [len(path) for path in paths]
            
            # Retrieve the index of the shortest path and store it in the attribute
            self._shortest_path = paths[np.argmin(paths_lengths)]
            
            # logger.debug(f"Shortest path by stops selected ({len(self._shortest_path)} stations): {self._shortest_path}")
        else :
            # logger.warning(f"No valid path found for airport '{self._arrival_airport}' from '{self._departure_station}'.")
            self._shortest_path = None
            

    def set_arrival_station(self) -> None:
        """
        Sets the arrival station using the last element 
        of the precomputed shortest path.

        !!! The shortest path has to be computed !!!
        """
        if self._shortest_path:
            self._arrival_station = self._shortest_path[-1]
            # logger.debug(f"Arrival station successfully set to: {self._arrival_station}")
        else:
            # logger.warning("The shortest path has not been computed yet.")
            self._arrival_station = None
    
