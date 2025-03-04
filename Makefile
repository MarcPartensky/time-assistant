# include .env
# export

run:
	# uv run python ./time-assistant/server.py
	# uv run uvicorn app.main:app --reload
	# hypercorn app.main --bind 0.0.0.0 --reload --log-level debug
	# hypercorn -c hypercorn.toml --reload app.main
	# python -m app.main
	granian app.main --interface asgi --host 0.0.0.0 --access-log --reload
test:
	uv run pytest tests/
export:
	poetry export -o requirements.txt
