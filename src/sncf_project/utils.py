import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data
def load_dataset(file_path: str, sep: str = ";") -> pd.DataFrame:
    """ "Load a CSV et return"""
    try:
        logger.info(f"Loading the dataset : {file_path}")
        df = pd.read_csv(file_path, sep=sep)
        logger.info(f"The {file_path} with {len(df)} row has been loaded")
        return df
    except FileNotFoundError:
        logger.error(f"File not found : {file_path}")
    except pd.errors.EmptyDataError:
        logger.error(f"The file at {file_path} is empty.")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse CSV structure in {file_path}: {e}")
        return None
    except PermissionError:
        logger.error(f"Permission denied while attempting to read: {file_path}")
        return None
