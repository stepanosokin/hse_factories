FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

ADD . /app

WORKDIR /app

RUN uv sync --locked

RUN uv run hse-factories.py