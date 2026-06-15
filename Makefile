.PHONY: install install-dev serve serve-dev lint format test coverage

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

serve:
	uv run server.py

serve-dev:
	uv run server.py --reload

lint:
	uv run black --check .

format:
	uv run black .

test:
	uv run pytest tests

coverage:
	uv run pytest --cov=src tests/ --cov-report=term-missing --cov-report=xml
