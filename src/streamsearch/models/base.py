"""Model abstractions for encoding video frames into embeddings."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import numpy as np


class BaseEncoder(ABC):
    """Abstract base encoder for frame embeddings."""

    @abstractmethod
    def encode(self, image: np.ndarray) -> np.ndarray:
        """Encode a single image into an embedding vector."""
        raise NotImplementedError

    @abstractmethod
    def encode_batch(self, images: List[np.ndarray]) -> np.ndarray:
        """Encode a batch of images into embedding vectors."""
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimensionality of the embedding vectors."""
        raise NotImplementedError
