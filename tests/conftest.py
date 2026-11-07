import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

os.environ.setdefault("SS_QDRANT_HOST", "localhost")
os.environ.setdefault("SS_REDIS_HOST", "localhost")
os.environ.setdefault("SS_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
