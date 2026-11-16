from dataclasses import dataclass
import logging
import pandas as pd
from settings import STATION_TO_AIRPORT

logger = logging.getLogger(__name__)

@dataclass
class Trip:
    """
    Class representing a specific rail link,
    including departure, arrival, date, and associated punctuality metrics.

    Attributes
    ----------
    _departure_station : str
        The name of the departure train station.
    _arrival_station : str
        The name of the arrival train station.
    _trip_date : str
        The scheduled date of the trip (format: YYYY-MM-DD).
    _arrival_airport : str, optional
        The associated airport at the arrival station, if a correspondence exists.
    
    Class Attributes
    ----------------
    __df : pd.DataFrame
        Preprocessed main SNCF dataset loaded once at the class level.
    __df_airport_seasonality : pd.DataFrame
        Preprocessed aggregated seasonality metrics for airport-connected routes.
    __unique_link : pd.DataFrame
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
    get_possible_arrival_stations() -> list of str
        Lists all possible arrival train stations matching the target arrival airport.

    Notes
    -----
    - Acts as a core entity for evaluating train delays and connection risks.
    - Warning : we have to loading data before building any object such that for instance :
    with streamlit.spinner("Chargement des données SNCF en cours..."):
    Trip.load_datasets()

    Example
    -------
    #1 Load preprocessed datasets at startup :
    Trip.load_datasets()

    #2 Create a trip instance :
    trip = Trip(
        _departure_station="LYON PART DIEU",
        _arrival_station="PARIS LYON",
        _trip_date="2026-07-15",
        _arrival_airport="PARIS-ORLY / PARIS-CHARLES-DE-GAULLE"
    )
    #3 Get all stations matching the target airport :
    stations = trip.get_possible_arrival_stations()

    """
    _departure_station: str
    _arrival_station: str
    _trip_date: str
    _arrival_airport: str = None

    __df: pd.DataFrame = None
    __df_airport_seasonality: pd.DataFrame = None
    __unique_link: pd.DataFrame = None


    # Class method

    @classmethod
    def load_datasets(cls, 
                      df_path: str = "data/processed_df.csv", 
                      seasonality_path: str = "data/processed_airport_seasonality.csv", 
                      links_path: str = "data/processed_unique_links.csv") -> None:
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
        logger.debug("Loading preprocessed datasets for Trip at class level")
        
        if not hasattr(cls, "__df") or cls.__df is None:
            cls.__df = pd.read_csv(df_path)
            
        if not hasattr(cls, "__df_airport_seasonality") or cls.__df_airport_seasonality is None:
            cls.__df_airport_seasonality = pd.read_csv(seasonality_path)
            
        if not hasattr(cls, "__unique_link") or cls.__unique_link is None:
            cls.__unique_link = pd.read_csv(links_path)


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
        
        if not self._arrival_airport:
            return []

        # Parcourt le dictionnaire importé de settings.py pour extraire les gares correspondantes
        return [
            station for station, airport in STATION_TO_AIRPORT.items() 
            if airport == self._arrival_airport
        ]
    
