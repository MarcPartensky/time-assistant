FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get purge -y curl && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app
RUN pip install uv granian
COPY requirements.txt .
RUN uv pip install -r requirements.txt --target /opt/dependencies


FROM python:3.12-slim

ENV PYTHONPATH="/opt/dependencies:$PYTHONPATH"
COPY --from=builder /opt/dependencies /opt/dependencies
RUN pip install granian

COPY ./tests/health.py /tests/health.py
COPY ./app /app

# HEALTHCHECK --interval=5s CMD wget --spider http://localhost:8000/live || exit 1
HEALTHCHECK --interval=5s CMD python /tests/health.py

# ENTRYPOINT ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--http", "auto", "app.main:app"]
ENTRYPOINT ["python", "-m", "app.main"]
