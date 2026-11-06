"""Pytest configuration and shared fixtures."""

import pytest

from src.streamsearch.models.clip_encoder import CLIPEncoder


@pytest.fixture
def encoder():
    return CLIPEncoder(model_name="ViT-B/32", device="cpu")
