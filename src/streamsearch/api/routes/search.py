"""Search routes."""

from fastapi import APIRouter, Depends

from src.streamsearch.api.dependencies import get_encoder, get_store
from src.streamsearch.api.schemas import SearchRequest, SearchResponse, SearchResult
from src.streamsearch.models.clip_encoder import CLIPEncoder
from src.streamsearch.storage.qdrant_store import QdrantStore

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    encoder: CLIPEncoder = Depends(get_encoder),
    store: QdrantStore = Depends(get_store),
):
    # Placeholder: encode text query using CLIP text model
    from transformers import CLIPProcessor, CLIPModel
    import torch

    config_encoder = encoder
    processor = CLIPProcessor.from_pretrained(f"openai/{config_encoder.model_name}")
    model = CLIPModel.from_pretrained(f"openai/{config_encoder.model_name}").to(config_encoder.device)
    inputs = processor(text=[request.query], return_tensors="pt").to(config_encoder.device)
    with torch.no_grad():
        features = model.get_text_features(**inputs)
        features = features / features.norm(p=2, dim=-1, keepdim=True)
    vector = features.cpu().numpy().astype("float32")[0].tolist()

    results = store.search(vector=vector, limit=request.limit, stream_id=request.stream_id)
    return SearchResponse(
        results=[SearchResult(id=r["id"], score=r["score"], payload=r["payload"]) for r in results]
    )
