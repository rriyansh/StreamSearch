"""Application configuration loading from YAML and environment."""

import os
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "config.yaml"


def _env_override(value):
    if isinstance(value, str):
        env_value = os.environ.get(value.upper())
        if env_value is not None:
            return env_value
    return value


def _resolve_overrides(data):
    if isinstance(data, dict):
        return {k: _resolve_overrides(_env_override(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve_overrides(_env_override(v)) for v in data]
    return _env_override(data)


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    """Load configuration from a YAML file with environment overrides."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return _resolve_overrides(data)
