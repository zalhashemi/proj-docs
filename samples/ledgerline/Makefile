.PHONY: dev test lint migrate

dev:
	uvicorn app.main:app --reload

test:
	pytest --cov=app

lint:
	ruff check .

migrate:
	alembic upgrade head
