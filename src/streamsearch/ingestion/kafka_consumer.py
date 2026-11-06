"""Kafka consumer for video ingestion events."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict

from kafka import KafkaConsumer


class KafkaVideoConsumer:
    """Consume ingestion events from Kafka."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "video.ingest",
        group_id: str = "streamsearch-worker",
    ) -> None:
        self.topic = topic
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )

    def consume(self, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        for message in self.consumer:
            handler(message.key, message.value)

    def close(self) -> None:
        self.consumer.close()
