from dataclasses import dataclass
# import logging

# logger = logging.getLogger(__name__)

@dataclass
class Traveler:
    """
    Class representing a traveler and their journey criteria,
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
        __departure_station="LYON PART DIEU",
        __trip_date="2026-07-15",
        __arrival_airport="LYON SAINT-EXUPÉRY"
    )

    #2 Access attributes via getters :
    station = traveler.get_departure_station
    """
    __departure_station: str
    __trip_date: str
    __arrival_airport: str

    # Getters

    @property
    def get_departure_station(self) -> str:
        """
        Returns the departure train station.

        Returns
        -------
        str
            The name of the departure train station.
        """
        # logger.debug("Getting departure station for traveler")
        return self.__departure_station

    @property
    def get_trip_date(self) -> str:
        """
        Returns the scheduled date of the trip.

        Returns
        -------
        str
            The scheduled date of the trip (format: YYYY-MM-DD).
        """
        # logger.debug("Getting trip date for traveler")
        return self.__trip_date

    @property
    def get_arrival_airport(self) -> str:
        """
        Returns the target arrival airport.

        Returns
        -------
        str
            The target airport the traveler intends to reach.
        """
        # logger.debug("Getting arrival airport for traveler")
        return self.__arrival_airport