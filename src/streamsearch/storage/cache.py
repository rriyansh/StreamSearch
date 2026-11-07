"""Redis-backed query cache."""

import hashlib
import json
from typing import Any

import redis

from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class QueryCache:
    def __init__(self) -> None:
        settings = get_settings()
        self.ttl = settings.cache_ttl
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._client.ping()
            self._enabled = True
        except Exception as exc:
            logger.warning("Redis cache disabled: %s", exc)
            self._client = None
            self._enabled = False

    @staticmethod
    def _key(prefix: str, payload: dict[str, Any]) -> str:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return f"ss:{prefix}:{digest}"

    def get(self, prefix: str, payload: dict[str, Any]) -> Any:
        if not self._enabled:
            return None
        raw = self._client.get(self._key(prefix, payload))
        return json.loads(raw) if raw else None

    def set(self, prefix: str, payload: dict[str, Any], value: Any) -> None:
        if not self._enabled:
            return
        self._client.setex(self._key(prefix, payload), self.ttl, json.dumps(value))
