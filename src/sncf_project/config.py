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
