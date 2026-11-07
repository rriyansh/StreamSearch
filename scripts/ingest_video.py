"""CLI: ingest a video through Kafka into Qdrant.

Usage:
    python scripts/ingest_video.py /path/to/video.mp4
"""

import argparse
import sys

from streamsearch.ingestion import IngestionPipeline
from streamsearch.logging_config import setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a video file")
    parser.add_argument("video", help="Path to video file")
    args = parser.parse_args()

    setup_logging()
    result = IngestionPipeline().ingest_video(args.video)
    print(f"Ingested video_id={result['video_id']} frames_sent={result['frames_sent']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
