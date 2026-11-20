import logging.config
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "logging_config.yaml"


def setup_logging(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Configure application logging from a YAML configuration file.

    Loads the logging dictionary configuration from ``config_path``. For any
    file-based handlers defined in the YAML file, relative paths are resolved
    against ``PROJECT_ROOT`` and missing parent directories (such as ``logs/``)
    are created automatically before applying ``logging.config.dictConfig``.
    Falls back to ``logging.basicConfig(level=logging.INFO)`` if the
    configuration file does not exist.

    Args:
        config_path (Path, optional): Path to the YAML logging configuration
            file. Defaults to ``DEFAULT_CONFIG_PATH``.

    Returns:
        None
    """
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)

        """ Create parent directories (e.g., logs/) for any file 
        handlers before dictConfig runs"""
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
