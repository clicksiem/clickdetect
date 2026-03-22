FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends cmake make gcc g++

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed
RUN uv python install 3.13

WORKDIR /app
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync 

FROM debian:bookworm-slim AS runtime
LABEL org.opencontainers.image.source https://github.com/clicksiem/clickdetect

COPY --from=builder /python /python
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["clickdetect"]
