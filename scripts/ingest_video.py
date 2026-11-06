#!/usr/bin/env python3
"""Ingest a video file into the StreamSearch pipeline."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.streamsearch.ingestion.pipeline import ingest_video  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a video file")
    parser.add_argument("video_path", type=Path, help="Path to the video file")
    parser.add_argument("--stream-id", type=str, default=None, help="Stream identifier")
    args = parser.parse_args()

    if not args.video_path.exists():
        print(f"Video not found: {args.video_path}", file=sys.stderr)
        return 1

    ingest_video(args.video_path, stream_id=args.stream_id)
    print(f"Ingested {args.video_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
