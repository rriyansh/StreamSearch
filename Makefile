.PHONY: help install up down logs build test lint format clean ingest

help:
	@echo "StreamSearch Makefile"
	@echo "  make install    - install python deps"
	@echo "  make up         - start all services"
	@echo "  make down       - stop all services"
	@echo "  make logs       - follow logs"
	@echo "  make build      - rebuild docker images"
	@echo "  make test       - run tests"
	@echo "  make lint       - run linters"
	@echo "  make format     - format code"
	@echo "  make clean      - remove containers and volumes"
	@echo "  make ingest VIDEO=path - ingest a video file"

install:
	pip install -r requirements.txt -r requirements-dev.txt

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build --no-cache

test:
	pytest tests/ -v

lint:
	ruff check src/ ui/ worker/ tests/
	mypy src/

format:
	ruff format src/ ui/ worker/ tests/
	ruff check --fix src/ ui/ worker/ tests/

clean:
	docker compose down -v --remove-orphans

ingest:
	python scripts/ingest_video.py $(VIDEO)
