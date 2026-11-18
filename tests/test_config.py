import logging
import logging.config
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sncf_project.config import setup_logging


def test_setup_logging_when_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Create a config file"""
    configs = tmp_path / "configs"
    configs.mkdir()
    configs_file = configs / "logging_config.yaml"
    configs_file.write_text(
        "version: 1\ndisable_existing_loggers: false\nroot:\n   level: DEBUG\n",
        encoding="utf-8",
    )

    """Change directory for the test"""
    monkeypatch.chdir(tmp_path)
    mock_dict_config = MagicMock()
    monkeypatch.setattr(logging.config, "dictConfig", mock_dict_config)

    """Run the setup_logging()"""

    setup_logging()

    mock_dict_config.assert_called_once_with(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "root": {"level": "DEBUG"},
        }
    )


def test_setup_logging_when_file_not_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Change directory for the test"""
    monkeypatch.chdir(tmp_path)
    mock_dict_config = MagicMock()
    monkeypatch.setattr(logging, "basicConfig", mock_dict_config)

    """Run the setup_logging()"""

    setup_logging()

    mock_dict_config.assert_called_once_with(level=logging.INFO)
