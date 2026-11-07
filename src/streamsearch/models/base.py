"""Abstract encoder interface."""

from abc import ABC, abstractmethod
from typing import List

import numpy as np
from PIL import Image


class BaseEncoder(ABC):
    """Interface for image/text encoders producing joint embeddings."""

    @property
    @abstractmethod
    def vector_size(self) -> int:
        """Dimensionality of the produced embeddings."""

    @abstractmethod
    def encode_image(self, image: Image.Image) -> np.ndarray:
        """Return a normalized 1-D vector for a single image."""

    @abstractmethod
    def encode_images(self, images: List[Image.Image]) -> np.ndarray:
        """Return an array of shape (N, vector_size) for a batch of images."""

    @abstractmethod
    def encode_text(self, text: str) -> np.ndarray:
        """Return a normalized 1-D vector for a text query."""
