FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

#ADD . /app

WORKDIR /app
COPY pyproject.toml uv.lock ./


# RUN uv build
RUN apt-get -y update
RUN apt-get -y install git

RUN uv sync --locked
# RUN uv sync

COPY . .

CMD ["uv", "run", "hse-factories.py"]