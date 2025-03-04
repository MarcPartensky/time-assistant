FROM python:3.12-alpine

ENV PORT=8000
ENV HOST=0.0.0.0

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./app /app
COPY hypercorn.toml ./

ENTRYPOINT ["hypercorn", "-c", "hypercorn.toml", "app.main"]
