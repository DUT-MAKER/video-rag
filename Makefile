FRONTEND_DIR=web
.PHONY: help dev-api dev-web docker-dev-web migrate create-migration test install-hooks lint

help:
	@echo "Available commands:"
	@echo "  make dev-api        - Start the local development server (uvicorn)"
	@echo "  make dev-web        - Start the frontend development server (Next.js)"
	@echo "  make docker-dev-web - Start the frontend development server with Docker Compose"
	@echo "  make migrate        - Run all database migrations (locally using uv)"
	@echo "  make create-migration DESC=\"msg\" - Create a new migration revision (locally)"
	@echo "  make test           - Run backend test suite (locally)"
	@echo "  make install-hooks  - Install git pre-commit hooks"
	@echo "  make lint           - Run all formatting, linting, and tests (same as pre-commit)"

dev-api:
	cd ./backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-web:
	cd ./$(FRONTEND_DIR) && pnpm dev

docker-dev-web:
	docker compose up web

migrate:
	cd ./backend && uv run alembic upgrade head

create-migration:
	@if [ -z "$(DESC)" ]; then echo "Error: Please specify DESC, e.g., make create-migration DESC=\"add new table\""; exit 1; fi
	cd ./backend && uv run alembic revision --autogenerate -m "$(DESC)"

test:
	cd ./backend && uv run pytest

install-hooks:
	mkdir -p .git/hooks
	cp .githooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Git pre-commit hooks installed successfully!"

lint:
	./.githooks/pre-commit

