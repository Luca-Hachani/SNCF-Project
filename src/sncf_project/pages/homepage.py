"""Homepage view for the SNCF Project Streamlit application.

Displays the project overview, navigation links to the data visualization and
trip planning pages, and logs unique visitor connection metadata once per session.
"""

import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger("sncf_project.pages.homepage")


def get_client_ip() -> str:
    """Retrieve the visitor's IP address from the Streamlit request context.

    Checks the ``X-Forwarded-For`` HTTP header first (for reverse-proxy setups),
    then falls back to ``st.context.ip_address``, and finally defaults to
    ``"127.0.0.1 (local)"`` when running locally without proxy headers.

    Returns:
        str: The resolved client IP address string.
    """
    # Get Header
    forwarded_for = st.context.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    ip = getattr(st.context, "ip_address", None)
    if ip:
        return ip

    return "127.0.0.1 (local)"


st.title("Welcome to our SNCF Project")
st.subheader("Catch your flight on time by choosing the most reliable TGV route!")

# pages/ -> sncf_project/ -> src/ project_root/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
HOMEPAGE_BANNER_PATH = PROJECT_ROOT / "assets" / "homepage_banner.jpg"


left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    st.image(HOMEPAGE_BANNER_PATH, width=500)


st.markdown(
    """
    Welcome to our platform! \n
    Built by a **team of 3 developers from the MS IA**, this application leverages official **SNCF Open Data** to help you plan stress-free connections between your home city  and your departure
    airport.
    """
)

st.divider()

st.markdown("### 📊 Explore the SNCF Dataset")
st.markdown(
    """
        Curious about the SNCF dataset ?
        * Inspect monthly **TGV regularity and punctuality** metrics across France
        * Visualize **stations locations**
        * Filter delays by **TGV line, stations, and travel date**
    """
)
st.page_link(
    "pages/data_visualization.py",
    label="Open the visualization tab",
    icon="📊",
)

st.divider()

st.markdown("### 🧭 How does our planning system work?")
st.markdown(
    """
    Planning a holidays by plane ? Our tool builds your door-to-airport itinery by TGV:
    1. Select your **departure airport** and your **departure city** (via search or geolocation)
    2. Discover the closest **TGV stations** from your departure city
    3. **Compare TGV line reliability & delay predictions** so you can schedule the safest ride to the airport!
    """
)
st.page_link(
    "pages/search_form.py",
    label="Plan your next TGV trip",
    icon="🔍",
)
st.divider()

st.info(
    "💡 **Spend all the time you want on our website.** \n "
    "**Have a great time exploring it!** If you spot anything or have ideas to improve the tool, don't hesitate to send us your feedback.",
)

if "visitor_logged" not in st.session_state:
    client_ip = get_client_ip()
    user_agent = st.context.headers.get("User-Agent", "unknown")
    logger.info("New visitor connected | IP=%s | User-Agent=%s", client_ip, user_agent)
    st.session_state["visitor_logged"] = True
