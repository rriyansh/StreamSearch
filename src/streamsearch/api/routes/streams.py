"""Manage registered live streams (placeholder persistence in-memory)."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from ..schemas import StreamInfo, StreamRegisterRequest

router = APIRouter()
_STREAMS: dict[str, StreamInfo] = {}


@router.post("", response_model=StreamInfo)
def register(req: StreamRegisterRequest) -> StreamInfo:
    sid = str(uuid.uuid4())
    info = StreamInfo(
        id=sid,
        stream_url=req.stream_url,
        label=req.label,
        status="registered",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _STREAMS[sid] = info
    return info


@router.get("", response_model=list[StreamInfo])
def list_streams() -> list[StreamInfo]:
    return list(_STREAMS.values())
