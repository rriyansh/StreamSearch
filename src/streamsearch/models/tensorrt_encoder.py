"""TensorRT-accelerated encoder. Falls back to CLIPEncoder when TRT is unavailable."""

from pathlib import Path
from typing import List

import numpy as np
from PIL import Image

from ..logging_config import get_logger
from .base import BaseEncoder
from .clip_encoder import CLIPEncoder

logger = get_logger(__name__)


class TensorRTEncoder(BaseEncoder):
    """
    Wraps a TensorRT engine that exposes `encode_image` and `encode_text`.

    The engine must be built by `scripts/export_tensorrt.py`. If the engine
    file is missing or TensorRT isn't installed, this class transparently
    falls back to `CLIPEncoder`.
    """

    def __init__(self, engine_path: str, model_name: str = "ViT-B/32", device: str = "auto") -> None:
        self._fallback: CLIPEncoder | None = None
        self._session = None

        try:
            import pycuda.driver as cuda  # noqa: F401
            import pycuda.autoinit  # noqa: F401
            import tensorrt as trt  # noqa: F401

            path = Path(engine_path)
            if not path.exists():
                raise FileNotFoundError(f"TensorRT engine not found: {engine_path}")

            import tensorrt as trt

            trt_logger = trt.Logger(trt.Logger.WARNING)
            runtime = trt.Runtime(trt_logger)
            with path.open("rb") as f:
                engine = runtime.deserialize_cuda_engine(f.read())
            if engine is None:
                raise RuntimeError("Failed to deserialize TensorRT engine")
            self._engine = engine
            self._context = engine.create_execution_context()
            self._vector_size = int(engine.get_tensor_shape("output")[1])
            self._engine_path = str(path)
            logger.info("TensorRT encoder loaded: %s", engine_path)
        except Exception as exc:  # pragma: no cover (defensive)
            logger.warning("TensorRT unavailable (%s). Falling back to CLIPEncoder.", exc)
            self._fallback = CLIPEncoder(model_name=model_name, device=device)
            self._vector_size = self._fallback.vector_size

    @property
    def vector_size(self) -> int:
        return self._vector_size

    def _infer(self, tensor: np.ndarray) -> np.ndarray:  # pragma: no cover (needs TRT)
        import pycuda.driver as cuda
        import tensorrt as trt

        input_name = self._engine.get_tensor_name(0)
        output_name = self._engine.get_tensor_name(1)
        input_shape = tuple(self._context.get_tensor_shape(input_name))
        assert tuple(tensor.shape) == input_shape, (tensor.shape, input_shape)

        stream = cuda.Stream()
        d_input = cuda.mem_alloc(tensor.nbytes)
        out_shape = tuple(self._context.get_tensor_shape(output_name))
        out_dtype = trt.nptype(self._engine.get_tensor_dtype(output_name))
        output_host = np.empty(out_shape, dtype=out_dtype)
        d_output = cuda.mem_alloc(output_host.nbytes)

        cuda.memcpy_htod_async(d_input, tensor, stream)
        self._context.set_tensor_address(input_name, int(d_input))
        self._context.set_tensor_address(output_name, int(d_output))
        self._context.execute_async_v3(stream_handle=stream.handle)
        cuda.memcpy_dtoh_async(output_host, d_output, stream)
        stream.synchronize()
        return output_host

    def encode_image(self, image: Image.Image) -> np.ndarray:
        if self._fallback is not None:
            return self._fallback.encode_image(image)
        # NOTE: production code should reuse CLIP's preprocess; simplified here.
        import torch
        from torchvision import transforms
        tfm = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.48145466, 0.4578275, 0.40821073),
                std=(0.26862954, 0.26130258, 0.27577711),
            ),
        ])
        arr = tfm(image.convert("RGB")).unsqueeze(0).numpy().astype("float32")
        out = self._infer(arr)[0]
        out = out / np.linalg.norm(out)
        return out.astype("float32")

    def encode_images(self, images: List[Image.Image]) -> np.ndarray:
        if self._fallback is not None:
            return self._fallback.encode_images(images)
        return np.stack([self.encode_image(img) for img in images]) if images else np.empty(
            (0, self._vector_size), dtype="float32"
        )

    def encode_text(self, text: str) -> np.ndarray:
        # Text encoder is not ported to TensorRT in this build; defer to CLIP.
        if self._fallback is None:
            self._fallback = CLIPEncoder()
        return self._fallback.encode_text(text)
