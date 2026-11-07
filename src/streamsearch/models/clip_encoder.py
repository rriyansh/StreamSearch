"""CLIP encoder — the default, PyTorch-backed implementation."""

from typing import List

import clip
import numpy as np
import torch
from PIL import Image

from ..logging_config import get_logger
from .base import BaseEncoder

logger = get_logger(__name__)


class CLIPEncoder(BaseEncoder):
    def __init__(self, model_name: str = "ViT-B/32", device: str = "auto") -> None:
        self._device = "cuda" if (device == "auto" and torch.cuda.is_available()) else (
            device if device != "auto" else "cpu"
        )
        logger.info("Loading CLIP model %s on %s", model_name, self._device)
        self._model, self._preprocess = clip.load(model_name, device=self._device)
        self._model.eval()
        self._vector_size = self._model.visual.output_dim

    @property
    def vector_size(self) -> int:
        return self._vector_size

    @torch.no_grad()
    def encode_image(self, image: Image.Image) -> np.ndarray:
        tensor = self._preprocess(image.convert("RGB")).unsqueeze(0).to(self._device)
        features = self._model.encode_image(tensor)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().flatten().astype("float32")

    @torch.no_grad()
    def encode_images(self, images: List[Image.Image]) -> np.ndarray:
        if not images:
            return np.empty((0, self._vector_size), dtype="float32")
        batch = torch.stack([self._preprocess(img.convert("RGB")) for img in images]).to(self._device)
        features = self._model.encode_image(batch)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().astype("float32")

    @torch.no_grad()
    def encode_text(self, text: str) -> np.ndarray:
        tokens = clip.tokenize([text], truncate=True).to(self._device)
        features = self._model.encode_text(tokens)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().flatten().astype("float32")
