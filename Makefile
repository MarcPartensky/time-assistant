run:
	# uv run python ./time-assistant/server.py
	uv run uvicorn app.main:app --reload
test:
	uv run pytest tests/
export:
	poetry export -o requirements.txt
