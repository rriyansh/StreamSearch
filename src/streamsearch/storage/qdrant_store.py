"""Qdrant vector store abstraction."""

import uuid
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from ..config import get_settings
from ..logging_config import get_logger
from ..metrics import VECTOR_COUNT

logger = get_logger(__name__)


class QdrantStore:
    def __init__(
        self,
        vector_size: int | None = None,
        collection: str | None = None,
        client: QdrantClient | None = None,
    ) -> None:
        self.settings = get_settings()
        self.collection = collection or self.settings.qdrant_collection
        self.vector_size = vector_size or self.settings.qdrant_vector_size
        self.client = client or QdrantClient(
            host=self.settings.qdrant_host,
            port=self.settings.qdrant_port,
            api_key=self.settings.qdrant_api_key or None,
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection):
            return
        logger.info("Creating Qdrant collection '%s'", self.collection)
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        # Payload indexes (safe to call multiple times)
        for field, schema in [
            ("video_id", "keyword"),
            ("video_path", "keyword"),
            ("timestamp_sec", "float"),
        ]:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection,
                    field_name=field,
                    field_schema=schema,
                )
            except Exception:
                pass

    def upsert(self, vector: np.ndarray, payload: dict[str, Any], point_id: str | None = None) -> str:
        pid = point_id or str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=pid,
                    vector=vector.tolist(),
                    payload=payload,
                )
            ],
        )
        return pid

    def bulk_upsert(self, vectors: np.ndarray, payloads: list[dict[str, Any]]) -> None:
        points = [
            PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload=p)
            for v, p in zip(vectors, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points)
        VECTOR_COUNT.set(self.client.count(self.collection).count)

    def search(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        video_id: str | None = None,
        min_timestamp: float | None = None,
        max_timestamp: float | None = None,
    ) -> list[dict[str, Any]]:
        filter_conditions = []
        if video_id:
            filter_conditions.append(FieldCondition(key="video_id", match=MatchValue(value=video_id)))
        if min_timestamp is not None or max_timestamp is not None:
            filter_conditions.append(
                FieldCondition(
                    key="timestamp_sec",
                    range=Range(gte=min_timestamp, lte=max_timestamp),
                )
            )
        query_filter = Filter(must=filter_conditions) if filter_conditions else None

        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector.tolist(),
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        return [
            {
                "id": str(h.id),
                "score": float(h.score),
                "payload": h.payload or {},
            }
            for h in hits
        ]

    def count(self) -> int:
        return int(self.client.count(self.collection).count)
