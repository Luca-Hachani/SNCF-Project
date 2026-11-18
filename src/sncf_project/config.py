import logging.config
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "logging_config.yaml"


def setup_logging(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    """ "Load YAML configutation file stored configs/logging_config.yaml"""
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Create parent directories (e.g., logs/) for any file handlers before dictConfig runs
        for handler in config.get("handlers", {}).values():
            if "filename" in handler:
                log_path = Path(handler["filename"])
                if not log_path.is_absolute():
                    log_path = PROJECT_ROOT / log_path
                    handler["filename"] = str(log_path)
                log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


# PATH TO DATASETS
DATASET_RE_MEN_TGV_PATH = "data/regularite-mensuelle-tgv-aqst.csv"
DATASET_STATIONS_PATH = "data/liste-des-gares.csv"
DATASET_COMMUNES_PATH = "data/liste-communes-France.csv"


# French Airports data
FRENCH_AIRPORTS = AIRPORTS_DATA = {
    "CDG": {
        "name": "Paris Charles-de-Gaulle (CDG)",
        "lat": 49.0097,
        "lon": 2.5479,
        "stations": [
            "PARIS EST",
            "PARIS LYON",
            "PARIS MONTPARNASSE",
            "PARIS NORD",
            "PARIS VAUGIRARD",
        ],
    },
    "ORY": {
        "name": "Paris Orly (ORY)",
        "lat": 48.7262,
        "lon": 2.3652,
        "stations": [
            "PARIS EST",
            "PARIS LYON",
            "PARIS MONTPARNASSE",
            "PARIS NORD",
            "PARIS VAUGIRARD",
        ],
    },
    "NCE": {
        "name": "Nice Côte d'Azur (NCE)",
        "lat": 43.6584,
        "lon": 7.2159,
        "stations": ["NICE VILLE"],
    },
    "LYS": {
        "name": "Lyon-Saint-Exupéry (LYS)",
        "lat": 45.7256,
        "lon": 5.0811,
        "stations": ["LYON PART DIEU"],
    },
    "MRS": {
        "name": "Marseille Provence (MRS)",
        "lat": 43.4393,
        "lon": 5.2214,
        "stations": ["MARSEILLE ST CHARLES"],
    },
    "TLS": {
        "name": "Toulouse-Blagnac (TLS)",
        "lat": 43.6291,
        "lon": 1.3638,
        "stations": ["TOULOUSE MATABIAU"],
    },
    "BOD": {
        "name": "Bordeaux-Mérignac (BOD)",
        "lat": 44.8283,
        "lon": -0.7156,
        "stations": ["BORDEAUX ST JEAN"],
    },
    "NTE": {
        "name": "Nantes Atlantique (NTE)",
        "lat": 47.1532,
        "lon": -1.6107,
        "stations": ["NANTES"],
    },
    "BSL": {
        "name": "Bâle-Mulhouse-Freiburg (BSL/MLH)",
        "lat": 47.5900,
        "lon": 7.5299,
        "stations": ["MULHOUSE VILLE"],
    },
    "LIL": {
        "name": "Lille-Lesquin (LIL)",
        "lat": 50.5619,
        "lon": 3.0894,
        "stations": ["LILLE"],
    },
    "MPL": {
        "name": "Montpellier-Méditerranée (MPL)",
        "lat": 43.5762,
        "lon": 3.9630,
        "stations": ["MONTPELLIER"],
    },
    "RNS": {
        "name": "Rennes-Bretagne (RNS)",
        "lat": 48.0695,
        "lon": -1.7348,
        "stations": ["RENNES"],
    },
    "SXB": {
        "name": "Strasbourg-Entzheim (SXB)",
        "lat": 48.5383,
        "lon": 7.6282,
        "stations": ["STRASBOURG"],
    },
    "BIQ": {
        "name": "Biarritz-Pays Basque (BIQ)",
        "lat": 43.4684,
        "lon": -1.5233,
        "stations": ["BIARRITZ"],
    },
    "BES": {
        "name": "Brest-Bretagne (BES)",
        "lat": 48.4479,
        "lon": -4.4185,
        "stations": ["BREST"],
    },
    "TLN": {
        "name": "Toulon-Hyères (TLN)",
        "lat": 43.0973,
        "lon": 6.1460,
        "stations": ["TOULON"],
    },
    # International hubs from your second list
    "FRA": {
        "name": "Aéroport de Francfort (FRA)",
        "lat": 50.0379,
        "lon": 8.5622,
        "stations": ["FRANCFORT"],
    },
    "ZRH": {
        "name": "Aéroport de Zurich (ZRH)",
        "lat": 47.4582,
        "lon": 8.5555,
        "stations": ["ZURICH"],
    },
    "GVA": {
        "name": "Aéroport de Genève (GVA)",
        "lat": 46.2370,
        "lon": 6.1092,
        "stations": ["GENEVE"],
    },
    "BCN": {
        "name": "Aéroport de Barcelone-El Prat (BCN)",
        "lat": 41.2974,
        "lon": 2.0833,
        "stations": ["BARCELONA"],
    },
}
