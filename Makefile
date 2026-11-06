.PHONY: setup install lint test format docker-up docker-down

PYTHON ?= python3
PIP ?= pip

setup: install
	@$(PYTHON) scripts/setup.sh

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt

lint:
	ruff check src/ ui/ worker/ scripts/ tests/
	black --check src/ ui/ worker/ scripts/ tests/

format:
	ruff format src/ ui/ worker/ scripts/ tests/
	black src/ ui/ worker/ scripts/ tests/

test:
	pytest

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
