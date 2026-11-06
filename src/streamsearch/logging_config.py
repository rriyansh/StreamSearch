"""Logging configuration using YAML dictConfig."""

import logging.config
from pathlib import Path

import yaml

DEFAULT_LOGGING_PATH = Path(__file__).resolve().parents[1] / "configs" / "logging.yaml"


def configure_logging(path: str | Path = DEFAULT_LOGGING_PATH) -> None:
    """Configure logging from a YAML file, falling back to basic config."""
    config_path = Path(path)
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level="INFO", format="%(asctime)s %(name)s %(levelname)s %(message)s")
