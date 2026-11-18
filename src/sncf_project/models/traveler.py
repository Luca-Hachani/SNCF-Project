import datetime
import logging
from dataclasses import dataclass, field

import pandas as pd

from sncf_project.utils import find_closest_stations

logger = logging.getLogger("utils")


@dataclass
class Traveler:
    """
    Class representing a traveler and their journeys criteria,
    used to filter and analyze train punctuality data relative to airport connections.

    Attributes
    ----------
    __departure_station : str
        The name of the departure train station.

    __trip_date : str
        The scheduled date of the trip (format: YYYY-MM-DD).

    __arrival_airport : str
        The target airport the traveler intends to reach, used to determine
        the most favorable arrival train station.

    Methods
    -------
    get_departure_station() -> str
        Returns the departure train station.

    get_trip_date() -> str
        Returns the scheduled date of the trip.

    get_arrival_airport() -> str
        Returns the target arrival airport.

    Notes
    -----
    - Integrates with the Streamlit interface to manage user trip criteria dynamically.

    Example
    -------
    #1 Create a traveler profile :
    traveler = Traveler(
        __departure_airport="LYS",
        __trip_date="2026-07-15",
        __departure_city="Caen"
    )

    #2 Access attributes via getters :
    station = traveler.get_departure_airport
    """

    __departure_airport: str
    __trip_date: datetime
    __departure_city: str
    __departure_station: list[str] | None = field(default=None, init=False)

    # Getters

    @property
    def get_departure_airport(self) -> str:
        """
        Returns the target departure airport.

        Returns
        -------
        str
            The target airport the traveler intends to reach.
        """
        logger.debug("Getting departure airport for traveler")
        return self.__departure_airport

    @property
    def get_trip_date(self) -> str:
        """
        Returns the scheduled date of the trip.

        Returns
        -------
        str
            The scheduled date of the trip (format: YYYY-MM-DD).
        """
        logger.debug("Getting trip date for traveler")
        return self.__trip_date

    @property
    def get_departure_city(self) -> str:
        """
        Returns the target arrival airport.

        Returns
        -------
        str
            The target airport the traveler intends to reach.
        """
        logger.debug("Getting departure city for traveler")
        return self.__departure_city

    @property
    def get_departure_station(self) -> list[str]:
        """
        Returns the departure train station.

        Returns
        -------
        str
            The name of the departure train station.
        """
        logger.debug("Getting departure station for traveler")
        return self.__departure_station

    # Get the station closest to the departure_city
    def compute_departure_station(
        self,
        df_reg: pd.DataFrame,
        df_stations: pd.DataFrame,
        df_communes: pd.DataFrame,
    ) -> None:
        """
        Compute the departure station.

        Returns
        -------
        None

        """

        # All info of the city departure
        departure_city_info = df_communes[
            df_communes["nom_de_la_commune"] == self.__departure_city
        ]
        logger.info(f"{departure_city_info}")
        logger.info(f"{type(departure_city_info)}")
        departure_geoloc = [
            float(departure_city_info["longitude"].iloc[0]),
            float(departure_city_info["latitude"].iloc[0]),
        ]

        # Match stations with geoloc from 2 SNCF Dataset
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

        # rename column X_WGS84/Y_WGS84 into lon/lat
        df_coords = df_stations[
            ["clean_station", "display_name", "X_WGS84", "Y_WGS84"]
        ].rename(columns={"X_WGS84": "lon", "Y_WGS84": "lat"})

        # Merge inner on stations
        df_pos_stations = pd.merge(df_reg, df_coords, on="clean_station", how="inner")

        # Drop duplicates
        df_unique_pos = (
            df_pos_stations[["lon", "lat", "display_name"]].drop_duplicates().dropna()
        )

        self.__departure_station = find_closest_stations(
            df_unique_pos, departure_geoloc, 3
        )
