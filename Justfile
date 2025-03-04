# include .env
# export

# uv run python ./time-assistant/server.py
# uv run uvicorn app.main:app --reload
# hypercorn app.main --bind 0.0.0.0 --reload --log-level debug
# hypercorn -c hypercorn.toml --reload app.main
# granian app.main --interface asgi --host 0.0.0.0 --access-log --reload
run:
	python -m app.main
test:
	uv run pytest tests/
push:
	uv export -o requirements.txt
	docker compose build
	docker compose push
