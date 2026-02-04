.PHONY: help build up down logs shell db-shell migrate test lint clean

# Default target
help:
	@echo "Elastic Newsroom Infrastructure - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build       Build all Docker images"
	@echo "  up          Start all services"
	@echo "  up-db       Start only database services (postgres, redis)"
	@echo "  down        Stop all services"
	@echo "  logs        View logs from all services"
	@echo "  shell       Open shell in identity service container"
	@echo "  db-shell    Open psql shell in postgres container"
	@echo "  migrate     Run database migrations"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  clean       Remove all containers and volumes"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start only database services
up-db:
	docker-compose up -d postgres redis

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Open shell in identity service
shell:
	docker-compose exec identity /bin/bash

# Open psql shell
db-shell:
	docker-compose exec postgres psql -U newsroom_user -d elastic_newsroom

# Run database migrations (all services)
migrate:
	docker-compose exec identity alembic upgrade head
	docker-compose exec discovery alembic upgrade head
	docker-compose exec pitch alembic upgrade head
	docker-compose exec payment alembic upgrade head
	docker-compose exec ml alembic upgrade head

# Run tests for all services
test:
	docker-compose exec identity pytest -v --cov=app --cov-report=term-missing
	docker-compose exec discovery pytest -v --cov=app --cov-report=term-missing
	docker-compose exec pitch pytest -v --cov=app --cov-report=term-missing
	docker-compose exec payment pytest -v --cov=app --cov-report=term-missing
	docker-compose exec ml pytest -v --cov=app --cov-report=term-missing

# Run tests for a specific service
test-identity:
	docker-compose exec identity pytest -v --cov=app --cov-report=term-missing

test-discovery:
	docker-compose exec discovery pytest -v --cov=app --cov-report=term-missing

test-pitch:
	docker-compose exec pitch pytest -v --cov=app --cov-report=term-missing

test-payment:
	docker-compose exec payment pytest -v --cov=app --cov-report=term-missing

test-ml:
	docker-compose exec ml pytest -v --cov=app --cov-report=term-missing

# Run linting
lint:
	docker-compose exec identity python -m flake8 app/
	docker-compose exec identity python -m mypy app/

# Clean up everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development: run services locally (requires local Python env)
dev-identity:
	cd services/identity && uvicorn app.main:app --reload --port 8001

dev-discovery:
	cd services/discovery && uvicorn app.main:app --reload --port 8002

dev-pitch:
	cd services/pitch && uvicorn app.main:app --reload --port 8003

dev-payment:
	cd services/payment && uvicorn app.main:app --reload --port 8004

dev-ml:
	cd services/ml && uvicorn app.main:app --reload --port 8005

# Initialize database (first time setup)
init-db:
	docker-compose up -d postgres redis
	@echo "Waiting for postgres to be ready..."
	@sleep 5
	docker-compose exec postgres psql -U newsroom_user -d elastic_newsroom -c "SELECT 1"
	@echo "Database is ready!"
