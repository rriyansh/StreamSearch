"""CLIP-based image encoder."""

from __future__ import annotations

from typing import List

import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from src.streamsearch.models.base import BaseEncoder


class CLIPEncoder(BaseEncoder):
    """Encode images using OpenAI CLIP."""

    def __init__(self, model_name: str = "ViT-B/32", device: str | None = None) -> None:
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = CLIPProcessor.from_pretrained(f"openai/{model_name}")
        self.model = CLIPModel.from_pretrained(f"openai/{model_name}").to(self.device)
        self.model.eval()
        self._embedding_dim = self.model.vision_model.config.hidden_size

    @torch.no_grad()
    def encode(self, image: np.ndarray) -> np.ndarray:
        pil_image = Image.fromarray(image).convert("RGB")
        inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)
        features = self.model.get_image_features(**inputs)
        features = features / features.norm(p=2, dim=-1, keepdim=True)
        return features.cpu().numpy().astype(np.float32)[0]

    @torch.no_grad()
    def encode_batch(self, images: List[np.ndarray]) -> np.ndarray:
        pil_images = [Image.fromarray(img).convert("RGB") for img in images]
        inputs = self.processor(images=pil_images, return_tensors="pt").to(self.device)
        features = self.model.get_image_features(**inputs)
        features = features / features.norm(p=2, dim=-1, keepdim=True)
        return features.cpu().numpy().astype(np.float32)

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
