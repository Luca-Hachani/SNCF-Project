import logging
import logging.config
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from sncf_project.config import setup_logging


def test_setup_logging_when_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Create logs directory and read a config file"""
    log_file = tmp_path / "logs" / "error.log"
    config_file = tmp_path / "logging_config.yaml"
    yaml_content = (
        "version: 1\n"
        "handlers:\n"
        "  console:\n"
        "    class: logging.StreamHandler\n"
        "  error_file:\n"
        "    class: logging.handlers.RotatingFileHandler\n"
        f"    filename: {log_file.as_posix()}\n"
        "root:\n"
        "  level: DEBUG\n"
    )
    config_file.write_text(yaml_content, encoding="utf-8")

    mock_dict_config = MagicMock()
    monkeypatch.setattr(logging.config, "dictConfig", mock_dict_config)

    """Run the setup_logging()"""
    setup_logging(config_path=config_file)

    assert log_file.parent.is_dir()

    mock_dict_config.assert_called_once_with(yaml.safe_load(yaml_content))







def test_setup_logging_when_missing_config_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Change directory for the test"""
    mock_dict_config = MagicMock()
    monkeypatch.setattr(logging, "basicConfig", mock_dict_config)

    """Run the setup_logging()"""

    setup_logging(config_path=tmp_path / "missing_config.yaml")

    mock_dict_config.assert_called_once_with(level=logging.INFO)
