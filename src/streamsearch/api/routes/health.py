"""Health and readiness endpoints."""

from fastapi import APIRouter

from ..dependencies import get_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    components: dict[str, str] = {}
    try:
        get_store().count()
        components["qdrant"] = "ok"
    except Exception as exc:
        components["qdrant"] = f"error: {exc}"
    status = "ok" if all(v == "ok" for v in components.values()) else "degraded"
    return {"status": status, "components": components}
