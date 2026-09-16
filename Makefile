.PHONY: help setup-be setup-ai dev-api dev-web docker-dev-web migrate create-migration test install-hooks lint run-ai

help:
	@echo "Available commands:"
	@echo "  make setup-be       - Install & sync Backend dependencies (uv sync)"
	@echo "  make setup-ai       - Install & sync AI microservice dependencies"
	@echo "  make dev-api        - Start the local Backend API server (uvicorn)"
	@echo "  make run-ai         - Start the local BentoML AI STT service"
	@echo "  make dev-web        - Start the frontend development server (Next.js)"
	@echo "  make docker-dev-web - Start the frontend development server with Docker Compose"
	@echo "  make migrate        - Run all database migrations (locally using uv)"
	@echo "  make create-migration DESC=\"msg\" - Create a new migration revision (locally)"
	@echo "  make test           - Run backend test suite (locally)"
	@echo "  make install-hooks  - Install git pre-commit hooks"
	@echo "  make lint           - Run all formatting, linting, and tests (same as pre-commit)"

setup-be:
	uv sync

setup-ai:
	cd services/stt_service && uv sync

dev-api:
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload

dev-web:
	cd ./web && pnpm dev


migrate:
	uv run alembic upgrade head

create-migration:
	@if [ -z "$(DESC)" ]; then echo "Error: Please specify DESC, e.g., make create-migration DESC=\"add new table\""; exit 1; fi
	uv run alembic revision --autogenerate -m "$(DESC)"

test:
	uv run pytest

install-hooks:
	mkdir -p .git/hooks
	cp .githooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Git pre-commit hooks installed successfully!"

lint:
	./.githooks/pre-commit

run-ai:
	cd services/stt_service && uv run bentoml serve service:WhisperXService --port 3001


