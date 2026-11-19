"""Main entry point for the SNCF Project Streamlit web application.

Initializes application-wide logging, configures Streamlit page metadata,
registers multipage navigation routes, and executes the active page.
"""

import logging
from pathlib import Path

import streamlit as st

from sncf_project.config import setup_logging

# app.py -> sncf_project/ -> src/ -> project_root/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGGING_CONFIG_PATH = PROJECT_ROOT / "configs" / "logging_config.yaml"


@st.cache_resource
def init_logging() -> bool:
    """Initialize process-wide logging configuration once per server lifecycle.

    Wraps ``setup_logging`` inside ``@st.cache_resource`` so that the YAML
    logging configuration is loaded once at startup rather than on every
    Streamlit script rerun.

    Returns:
        bool: Always returns ``True`` once logging configuration succeeds.
    """
    setup_logging(config_path=LOGGING_CONFIG_PATH)
    return True


init_logging()

logger = logging.getLogger("sncf_project.app")

st.set_page_config(
    page_title="SNCF Project",
    page_icon="🚄",
    layout="wide",
)

logger.info("Application started on user side")

# Register pages in the left sidebar menu
pg = st.navigation(
    [
        st.Page(
            "pages/homepage.py",
            title="Website description",
            icon="🏠",
            default=True,
        ),
        st.Page("pages/data_visualization.py", title="Visualize the Data", icon="📊"),
        st.Page("pages/search_form.py", title="Plan your TGV", icon="🔍"),
    ]
)

# Any st.sidebar elements placed in app.py appear across ALL pages
with st.sidebar:
    st.caption("SNCF Project - IADATA701")

pg.run()
