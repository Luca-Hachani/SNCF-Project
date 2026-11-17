import logging.config
from pathlib import Path

import yaml


def setup_logging():
    """ "Load YAML configutation file stored configs/logging_config.yaml"""
    config_path = Path("configs/logging_config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


# Initialize logging on import
setup_logging()

# PATH TO DATASETS
DATASET_RE_MEN_TGV_PATH = "data/regularite-mensuelle-tgv-aqst.csv"
DATASET_STATIONS_PATH = "data/liste-des-gares.csv"
DATASET_COMMUNES_PATH = "data/liste-communes-France.csv"

# French Airports data
FRENCH_AIRPORTS = {
    "CDG": {"name": "Paris Charles-de-Gaulle (CDG)", "lat": 49.0097, "lon": 2.5479},
    "ORY": {"name": "Paris Orly (ORY)", "lat": 48.7262, "lon": 2.3652},
    "NCE": {"name": "Nice Côte d'Azur (NCE)", "lat": 43.6584, "lon": 7.2159},
    "LYS": {"name": "Lyon-Saint-Exupéry (LYS)", "lat": 45.7256, "lon": 5.0811},
    "MRS": {"name": "Marseille Provence (MRS)", "lat": 43.4393, "lon": 5.2214},
    "TLS": {"name": "Toulouse-Blagnac (TLS)", "lat": 43.6291, "lon": 1.3638},
    "BOD": {"name": "Bordeaux-Mérignac (BOD)", "lat": 44.8283, "lon": -0.7156},
    "NTE": {"name": "Nantes Atlantique (NTE)", "lat": 47.1532, "lon": -1.6107},
    "BSL": {"name": "Bâle-Mulhouse-Freiburg (BSL/MLH)", "lat": 47.5900, "lon": 7.5299},
    "LIL": {"name": "Lille-Lesquin (LIL)", "lat": 50.5619, "lon": 3.0894},
    "MPL": {"name": "Montpellier-Méditerranée (MPL)", "lat": 43.5762, "lon": 3.9630},
    "RNS": {"name": "Rennes-Bretagne (RNS)", "lat": 48.0695, "lon": -1.7348},
    "SXB": {"name": "Strasbourg-Entzheim (SXB)", "lat": 48.5383, "lon": 7.6282},
    "BIQ": {"name": "Biarritz-Pays Basque (BIQ)", "lat": 43.4684, "lon": -1.5233},
    "BES": {"name": "Brest-Bretagne (BES)", "lat": 48.4479, "lon": -4.4185},
    "TLN": {"name": "Toulon-Hyères (TLN)", "lat": 43.0973, "lon": 6.1460},
}
