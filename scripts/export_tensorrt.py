"""Export CLIP image encoder to ONNX + TensorRT.

Usage:
    python scripts/export_tensorrt.py --output models/clip.engine

This script is best-effort. It requires a CUDA host with TensorRT 8.6+.
The StreamSearch API will fall back to PyTorch if the engine is missing.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="models/clip.engine")
    parser.add_argument("--model", default="ViT-B/32")
    parser.add_argument("--onnx", default="models/clip.onnx")
    args = parser.parse_args()

    try:
        import clip  # noqa: F401
        import torch
        import torch.onnx  # noqa: F401
        import tensorrt as trt
    except ImportError as exc:
        print(f"Missing dependency: {exc}", file=sys.stderr)
        return 1

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.onnx).parent.mkdir(parents=True, exist_ok=True)

    model, _ = clip.load(args.model, device="cuda")
    model.eval()

    dummy = torch.randn(1, 3, 224, 224, device="cuda")
    torch.onnx.export(
        model.visual,
        dummy,
        args.onnx,
        input_names=["image"],
        output_names=["output"],
        opset_version=17,
        do_constant_folding=True,
    )
    print(f"ONNX exported to {args.onnx}")

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser_trt = trt.OnnxParser(network, logger)
    with open(args.onnx, "rb") as f:
        if not parser_trt.parse(f.read()):
            for i in range(parser_trt.num_errors):
                print(parser_trt.get_error(i), file=sys.stderr)
            return 2

    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)
    if builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    engine = builder.build_serialized_network(network, config)
    with open(args.output, "wb") as f:
        f.write(engine)
    print(f"TensorRT engine written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
