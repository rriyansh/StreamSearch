#!/usr/bin/env python3
"""Export the CLIP encoder to a TensorRT engine."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.streamsearch.models.tensorrt_encoder import export_tensorrt  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Export CLIP encoder to TensorRT")
    parser.add_argument("--model", type=str, default="ViT-B/32", help="CLIP model name")
    parser.add_argument("--output", type=Path, default=Path("/models/encoder.engine"),
                        help="Output engine path")
    parser.add_argument("--precision", type=str, default="fp16", choices=["fp16", "fp32"],
                        help="TensorRT precision")
    args = parser.parse_args()

    export_tensorrt(model_name=args.model, output=args.output, precision=args.precision)
    print(f"TensorRT engine exported to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
