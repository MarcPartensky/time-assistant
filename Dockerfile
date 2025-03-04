# Stage 1: Builder (install dependencies)
FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get purge -y curl && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN uv pip install -r requirements.txt --target /app/dependencies

# Stage 2: Runtime (minimal image)
FROM python:3.12-slim

WORKDIR /app
COPY ./app /app

# Copy dependencies from builder
COPY --from=builder /dependencies /app/dependencies
# Add dependencies to Python path
ENV PYTHONPATH="/app/dependencies:$PYTHONPATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
