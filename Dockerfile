FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

#ADD . /app

WORKDIR /app
COPY . .

RUN uv sync --locked

CMD ["uv", "run", "hse-factories.py"]