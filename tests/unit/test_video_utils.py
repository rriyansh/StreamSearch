"""Unit tests for video utilities."""

from src.streamsearch.utils.video import list_videos
from src.streamsearch.utils.image import resize_image, to_rgb
import numpy as np


def test_resize_image():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    resized = resize_image(image, max_dim=50)
    assert max(resized.shape[:2]) <= 50


def test_to_rgb_gray():
    gray = np.zeros((10, 10), dtype=np.uint8)
    rgb = to_rgb(gray)
    assert rgb.shape == (10, 10, 3)


def test_list_videos_empty(tmp_path):
    assert list_videos(str(tmp_path)) == []
