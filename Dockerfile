FROM python:3.12-alpine

ENV PORT=8000
ENV HOST=0.0.0.0

WORKDIR /app

RUN pip install hypercorn

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./app /app

# ENV PATH="$PATH:/root/.local/bin"

WORKDIR /
COPY ./hypercorn.toml ./

ENTRYPOINT ["hypercorn", "-c", "hypercorn.toml", "app.main:app"]
