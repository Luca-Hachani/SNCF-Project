"""Domain model representing a traveler and their TGV-to-airport trip criteria."""

import datetime
import logging
from dataclasses import dataclass, field

import pandas as pd

from sncf_project.utils import find_closest_stations

logger = logging.getLogger("sncf_project.models.traveler")


@dataclass
class Traveler:
    """Represent a traveler and their trip criteria for TGV-to-airport matching.

    Stores the departure airport code, scheduled trip date, and departure city,
    and resolves the closest TGV departure stations from SNCF and commune
    geospatial datasets.

    Attributes:
        __departure_airport (str): IATA code or identifier of the departure
            airport (e.g., ``"LYS"``, ``"CDG"``).
        __trip_date (datetime.date): Scheduled date of the trip.
        __departure_city (str): Name of the traveler's departure commune/city.
        __departure_station (list[str] | None): Ordered list of the closest
            TGV departure station names computed by
            ``compute_departure_station``, or ``None`` before computation.

    Example:
        >>> import datetime
        >>> traveler = Traveler("LYS", datetime.date(2026, 7, 15), "Caen")
        >>> traveler.get_departure_airport
        'LYS'
    """

    __departure_airport: str
    __trip_date: datetime.date
    __departure_city: str
    __departure_station: list[str] | None = field(default=None, init=False)

    @property
    def get_departure_airport(self) -> str:
        """Return the traveler's target departure airport.

        Returns:
            str: The departure airport code or identifier.
        """
        logger.debug("Getting departure airport for traveler")
        return self.__departure_airport

    @property
    def get_trip_date(self) -> datetime.date:
        """Return the scheduled date of the trip.

        Returns:
            datetime.date: The scheduled trip date.
        """
        logger.debug("Getting trip date for traveler")
        return self.__trip_date

    @property
    def get_departure_city(self) -> str:
        """Return the traveler's departure city name.

        Returns:
            str: The departure city name.
        """
        logger.debug("Getting departure city for traveler")
        return self.__departure_city

    @property
    def get_departure_station(self) -> list[str] | None:
        """Return the closest departure TGV station names, if computed.

        Returns:
            list[str] | None: List of up to 3 closest station names, or
                ``None`` if ``compute_departure_station`` has not been called.
        """
        logger.debug("Getting departure station for traveler")
        return self.__departure_station

    def compute_departure_station(
        self,
        df_reg: pd.DataFrame,
        df_stations: pd.DataFrame,
        df_communes: pd.DataFrame,
    ) -> None:
        """Compute the 3 closest TGV departure stations to ``__departure_city``.

        Looks up the departure city's coordinates in ``df_communes``, matches
        active TGV departure stations between ``df_reg`` and ``df_stations``,
        deduplicates station coordinates by station name, and stores the 3
        nearest station names in ``__departure_station``.

        Args:
            df_reg (pd.DataFrame): TGV monthly regularity DataFrame containing
                ``"Gare de départ"``.
            df_stations (pd.DataFrame): Reference stations DataFrame containing
                ``"LIBELLE"``, ``"X_WGS84"``, and ``"Y_WGS84"``.
            df_communes (pd.DataFrame): French communes DataFrame containing
                ``"nom_de_la_commune"``, ``"longitude"``, and ``"latitude"``.

        Returns:
            None

        Raises:
            ValueError: If ``__departure_city`` is not found in ``df_communes``.
        """
        departure_city_info = df_communes[
            df_communes["nom_de_la_commune"] == self.__departure_city
        ]
        if departure_city_info.empty:
            msg = (
                f"Departure city not found in communes dataset: {self.__departure_city}"
            )
            logger.error(msg)
            raise ValueError(msg)

        departure_geoloc = [
            float(departure_city_info["longitude"].iloc[0]),
            float(departure_city_info["latitude"].iloc[0]),
        ]

        # Match stations with geoloc from 2 SNCF datasets without mutating inputs
        clean_reg_stations = (
            df_reg[["Gare de départ"]]
            .dropna()
            .assign(
                clean_station=lambda df: df["Gare de départ"].str.upper().str.strip()
            )
            .drop_duplicates(subset=["clean_station"])
        )

        clean_stations = pd.DataFrame(
            {
                "clean_station": (
                    df_stations["LIBELLE"]
                    .str.upper()
                    .str.strip()
                    .str.replace("-", " ", regex=False)
                ),
                "display_name": df_stations["LIBELLE"]
                .astype(str)
                .str.title()
                .str.strip(),
                "lon": pd.to_numeric(df_stations["X_WGS84"], errors="coerce"),
                "lat": pd.to_numeric(df_stations["Y_WGS84"], errors="coerce"),
            }
        )

        df_unique_pos = (
            clean_stations.merge(clean_reg_stations, on="clean_station", how="inner")
            .dropna(subset=["lon", "lat", "display_name", "Gare de départ"])
            .groupby("display_name", as_index=False)
            .agg(
                {
                    "lon": "mean",
                    "lat": "mean",
                    "Gare de départ": "first",
                }
            )
        )

        self.__departure_station = find_closest_stations(
            df_unique_pos, departure_geoloc, 3
        )
