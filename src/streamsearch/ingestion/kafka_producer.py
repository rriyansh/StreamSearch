"""Kafka producer for video ingestion events."""

from __future__ import annotations

import json
from typing import Any, Dict

from kafka import KafkaProducer


class KafkaVideoProducer:
    """Publish ingestion events to Kafka."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "video.ingest",
    ) -> None:
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )

    def send(self, key: str, payload: Dict[str, Any]) -> None:
        self.producer.send(self.topic, key=key, value=payload)
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()
