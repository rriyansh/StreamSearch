FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libglib2.0-0 libgl1 libsm6 libxext6 libxrender1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
RUN pip install -e .

COPY configs /app/configs

EXPOSE 8000

CMD ["uvicorn", "streamsearch.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
