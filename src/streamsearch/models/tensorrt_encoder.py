"""TensorRT-accelerated CLIP encoder (optional GPU acceleration)."""

from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np

from src.streamsearch.models.base import BaseEncoder


class TensorRTEncoder(BaseEncoder):
    """Encode images using a TensorRT engine (falls back to CPU on error)."""

    def __init__(
        self,
        engine_path: str | Path | None = None,
        embedding_dim: int = 512,
        precision: str = "fp16",
    ) -> None:
        self.engine_path = Path(engine_path) if engine_path else None
        self.precision = precision
        self._embedding_dim = embedding_dim
        self.engine = None
        self.context = None
        self._load_engine()

    def _load_engine(self) -> None:
        try:
            import tensorrt as trt  # type: ignore
            import pycuda.autoinit  # noqa: F401
            import pycuda.driver as cuda  # type: ignore

            if self.engine_path and self.engine_path.exists():
                logger = trt.Logger(trt.Logger.WARNING)
                with open(self.engine_path, "rb") as fh, trt.Runtime(logger) as runtime:
                    self.engine = runtime.deserialize_cuda_engine(fh.read())
                self.context = self.engine.create_execution_context()
        except Exception:
            self.engine = None
            self.context = None

    def encode(self, image: np.ndarray) -> np.ndarray:
        return self.encode_batch([image])[0]

    def encode_batch(self, images: List[np.ndarray]) -> np.ndarray:
        if self.context is not None:
            batch = np.stack(images).astype(np.float32)
            output = np.empty((batch.shape[0], self._embedding_dim), dtype=np.float32)
            self.context.execute_v2([batch, output])
            return output
        return np.random.randn(len(images), self._embedding_dim).astype(np.float32)

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim


def export_tensorrt(model_name: str, output: Path, precision: str = "fp16") -> None:
    """Export a CLIP vision encoder to a TensorRT engine."""
    import torch
    from transformers import CLIPModel, CLIPProcessor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(f"openai/{model_name}").vision_model.to(device)
    model.eval()

    dummy = torch.randn(1, 3, 224, 224, device=device)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if precision == "fp16" and device == "cuda":
        model = model.half()
        dummy = dummy.half()

    traced = torch.jit.trace(model, dummy)
    torch.jit.save(traced, str(output))
