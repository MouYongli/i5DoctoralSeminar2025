UV ?= uv
UV_PROJECT_ENV ?= .venv
PYTHON ?= $(UV) run python
PNPM ?= pnpm
COMPOSE_LOCAL ?= docker compose -f docker/docker-compose.local.yml --env-file docker/.env

.PHONY: install install-backend install-frontend clean cleanall docker-local-up docker-local-down docker-local-logs dev-back dev-front dev-worker dev db-init db-migrate

install: install-backend install-frontend

setup:
	cd backend && $(UV) venv --python 3.12

# Database setup - creates database if not exists (via docker)
db-init:
	@docker exec toyagent-postgresql psql -U postgres -c "CREATE DATABASE toyagent;" 2>/dev/null || echo "Database 'toyagent' already exists"

db-migrate:
	cd backend && $(UV) run alembic upgrade head

install-backend:
	cd backend && source $(UV_PROJECT_ENV)/bin/activate && UV_PROJECT_ENV=$(UV_PROJECT_ENV) $(UV) sync && UV_PROJECT_ENV=$(UV_PROJECT_ENV) $(UV) pip install -e .

install-frontend:
	cd frontend && $(PNPM) install

clean:
	find backend -name "__pycache__" -type d -prune -exec rm -rf {} +
	rm -rf backend/.pytest_cache backend/.ruff_cache frontend/.next

cleanall: clean
	rm -rf frontend/node_modules backend/.venv

docker-local-up:
	$(COMPOSE_LOCAL) up -d --build
	@sleep 2
	@$(MAKE) db-init

docker-local-down:
	$(COMPOSE_LOCAL) down -v

docker-local-logs:
	$(COMPOSE_LOCAL) logs -f

dev-back:
	cd backend && source $(UV_PROJECT_ENV)/bin/activate && UV_PROJECT_ENV=$(UV_PROJECT_ENV) $(UV) run toyagent

dev-worker:
	cd backend && source $(UV_PROJECT_ENV)/bin/activate && UV_PROJECT_ENV=$(UV_PROJECT_ENV) $(UV) run toyagent-worker

dev:
	$(MAKE) dev-back & $(MAKE) dev-worker & $(MAKE) dev-front

dev-front:
	cd frontend && $(PNPM) dev
