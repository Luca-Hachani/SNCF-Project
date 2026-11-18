"""Tests for the main Streamlit entry point (src/sncf_project/app.py)."""

from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "src" / "sncf_project" / "app.py"


def test_init_logging_calls_setup_logging() -> None:
    """Verify init_logging invokes setup_logging with LOGGING_CONFIG_PATH."""
    from sncf_project import app

    app.init_logging.clear()
    with patch("sncf_project.app.setup_logging") as mock_setup:
        result = app.init_logging()

    assert result is True
    mock_setup.assert_called_once_with(config_path=app.LOGGING_CONFIG_PATH)


def test_app_boots_and_renders_default_page() -> None:
    """Verify app.py runs without exceptions and renders the sidebar caption."""
    at = AppTest.from_file(str(APP_PATH), default_timeout=10)
    at.run()

    assert not at.exception
    captions = [cap.value for cap in at.sidebar.caption]
    assert "SNCF Project - IADATA701" in captions
