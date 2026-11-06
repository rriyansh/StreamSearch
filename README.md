# StreamSearch

StreamSearch is a video stream search engine built with CLIP embeddings, Qdrant vector storage, and a FastAPI backend. Ingest video streams, detect scenes, encode frames with CLIP (optionally TensorRT-accelerated), and search by text or image query.

## Project Structure

```
.env.example
.gitignore
.dockerignore
LICENSE
README.md
Makefile
pyproject.toml
requirements.txt
requirements-dev.txt
docker-compose.yml
docker-compose.prod.yml
.github/workflows/ci.yml
.github/workflows/docker.yml
configs/config.yaml
configs/logging.yaml
configs/prometheus.yml
docker/api.Dockerfile
docker/worker.Dockerfile
docker/ui.Dockerfile
docker/nginx.conf
scripts/setup.sh
scripts/ingest_video.py
scripts/export_tensorrt.py
scripts/health_check.sh
src/streamsearch/
src/streamsearch/models/
src/streamsearch/ingestion/
src/streamsearch/storage/
src/streamsearch/api/routes/
src/streamsearch/utils/
ui/app.py
worker/__init__.py
tests/unit/
tests/integration/
data/videos/.gitkeep
data/frames/.gitkeep
```

## Requirements

- Python 3.10+
- Docker & Docker Compose
- Qdrant vector database
- Apache Kafka
- TensorRT (optional, for GPU acceleration)

## Setup

```bash
make setup
```

## Run with Docker Compose

```bash
docker-compose up --build
```

## Run API locally

```bash
uvicorn src.streamsearch.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
pytest
```

## License

MIT License
