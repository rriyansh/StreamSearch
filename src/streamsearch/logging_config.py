"""Structured logging configuration."""

import logging
import logging.config
import os
from pathlib import Path

import yaml


def setup_logging(level: str | None = None) -> None:
    """Load logging configuration from YAML, falling back to a sane default."""
    config_path = Path("configs/logging.yaml")
    if config_path.exists():
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        )

    if level:
        logging.getLogger().setLevel(level)

    # Silence noisy libs
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
