"""Image utility helpers."""

from __future__ import annotations

import numpy as np
from PIL import Image


def resize_image(image: np.ndarray, max_dim: int = 1024) -> np.ndarray:
    """Resize image keeping aspect ratio."""
    pil = Image.fromarray(image)
    pil.thumbnail((max_dim, max_dim))
    return np.array(pil)


def to_rgb(image: np.ndarray) -> np.ndarray:
    """Ensure image is RGB."""
    if image.ndim == 2:
        return np.stack([image] * 3, axis=-1)
    if image.shape[2] == 4:
        return image[:, :, :3]
    return image
