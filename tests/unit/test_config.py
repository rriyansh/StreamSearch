"""Unit tests for configuration loading."""

from src.streamsearch.config import load_config


def test_load_config_defaults():
    config = load_config()
    assert "api" in config
    assert "models" in config
    assert "storage" in config
