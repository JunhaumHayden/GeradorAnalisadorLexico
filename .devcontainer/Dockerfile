FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash developer

WORKDIR /workspace

USER developer
