"""Qdrant vector store for embeddings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


class QdrantStore:
    """Store and search embeddings in Qdrant."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection: str = "video_embeddings",
        api_key: Optional[str] = None,
        vector_size: int = 512,
    ) -> None:
        self.host = host
        self.port = port
        self.collection = collection
        self.vector_size = vector_size
        self.client = QdrantClient(host=host, port=port, api_key=api_key)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]
        if self.collection not in names:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def upsert(self, points: List[Dict[str, Any]]) -> None:
        if not points:
            return
        payload_points = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p.get("payload", {}),
            )
            for p in points
        ]
        self.client.upsert(collection_name=self.collection, points=payload_points)

    def search(
        self,
        vector: List[float],
        limit: int = 10,
        stream_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue

        query_filter = None
        if stream_id:
            query_filter = Filter(
                must=[FieldCondition(key="stream_id", match=MatchValue(value=stream_id))]
            )

        result = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter,
        )
        return [
            {
                "id": str(r.id),
                "score": float(r.score),
                "payload": r.payload or {},
            }
            for r in result
        ]

    def count(self) -> int:
        info = self.client.get_collection(collection_name=self.collection)
        return int(info.points_count or 0)
