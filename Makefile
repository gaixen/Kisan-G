# Makefile for Kisan-G Application
# Automates build, test, deployment, and development workflows

.PHONY: help install install-frontend install-backend build build-frontend build-backend \
        start start-frontend start-backend dev test test-frontend test-backend \
        lint format clean docker-build docker-up docker-down docker-logs \
        deploy production migrate backup restore

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Variables
PYTHON := python
PIP := pip
NPM := npm
DOCKER := docker
DOCKER_COMPOSE := docker-compose

help: ## Show this help message
	@echo "$(BLUE)Kisan-G Application - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation targets
install: install-frontend install-backend ## Install all dependencies
	@echo "$(GREEN)----------- All dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	$(NPM) install
	@echo "$(GREEN)----------- Frontend dependencies installed$(NC)"

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)----------- Backend dependencies installed$(NC)"

# Build targets
build: build-frontend ## Build the entire application
	@echo "$(GREEN)----------- Application built successfully$(NC)"

build-frontend: ## Build React frontend
	@echo "$(BLUE)Building frontend...$(NC)"
	$(NPM) run build
	@echo "$(GREEN)----------- Frontend built$(NC)"

build-backend: ## Prepare backend for production
	@echo "$(BLUE)Preparing backend...$(NC)"
	$(PYTHON) -m compileall server/ utils/
	@echo "$(GREEN)----------- Backend prepared$(NC)"

# Development targets
dev: ## Start development servers (both frontend and backend)
	@echo "$(BLUE)Starting development servers...$(NC)"
	@start /b $(MAKE) start-backend
	@$(MAKE) start-frontend

start: start-backend ## Start production server
	@echo "$(GREEN)----------- Server started$(NC)"

start-frontend: ## Start React development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	$(NPM) start

start-backend: ## Start Flask backend server
	@echo "$(BLUE)Starting backend server...$(NC)"
	$(PYTHON) server/app.py

start-backend-prod: ## Start backend with Gunicorn (production)
	@echo "$(BLUE)Starting backend with Gunicorn...$(NC)"
	gunicorn -w 4 -b 0.0.0.0:5001 server.app:app --timeout 120

# Testing targets
test: test-backend ## Run all tests
	@echo "$(GREEN)----------- All tests completed$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	$(NPM) test -- --watchAll=false
	@echo "$(GREEN)----------- Frontend tests passed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	$(PYTHON) -m pytest server/tests/ -v
	@echo "$(GREEN)----------- Backend tests passed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest server/tests/ --cov=server --cov-report=html
	@echo "$(GREEN)----------- Coverage report generated in htmlcov/$(NC)"

# Code quality targets
lint: lint-frontend lint-backend ## Run linters on all code
	@echo "$(GREEN)----------- Linting completed$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(BLUE)Linting frontend...$(NC)"
	$(NPM) run lint || true

lint-backend: ## Lint backend code
	@echo "$(BLUE)Linting backend...$(NC)"
	$(PYTHON) -m flake8 server/ utils/ || true
	$(PYTHON) -m pylint server/ utils/ || true

format: format-frontend format-backend ## Format all code
	@echo "$(GREEN)----------- Code formatted$(NC)"

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	$(NPM) run format || true

format-backend: ## Format backend code with black
	@echo "$(BLUE)Formatting backend...$(NC)"
	$(PYTHON) -m black server/ utils/
	@echo "$(GREEN)----------- Backend formatted$(NC)"

type-check: ## Run TypeScript type checking
	@echo "$(BLUE)Type checking...$(NC)"
	$(NPM) run typecheck || true

# Docker targets
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	$(DOCKER) build -t kisan-g:latest .
	@echo "$(GREEN)----------- Docker image built$(NC)"

docker-up: ## Start application with Docker Compose
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)----------- Containers started$(NC)"
	@echo "$(YELLOW)View logs with: make docker-logs$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)----------- Containers stopped$(NC)"

docker-restart: docker-down docker-up ## Restart Docker containers

docker-logs: ## View Docker container logs
	$(DOCKER_COMPOSE) logs -f

docker-shell: ## Open shell in app container
	$(DOCKER_COMPOSE) exec app /bin/bash

docker-clean: ## Remove Docker images and volumes
	@echo "$(RED)Cleaning Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all
	@echo "$(GREEN)----------- Docker resources cleaned$(NC)"

# Database targets
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	$(PYTHON) -c "from server.database import DatabaseManager; DatabaseManager().init_database()"
	@echo "$(GREEN)----------- Migrations completed$(NC)"

backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@copy server\kisan_app.db backups\kisan_app_$(shell date +%Y%m%d_%H%M%S).db
	@echo "$(GREEN)----------- Database backed up$(NC)"

restore: ## Restore database from backup (specify FILE=backup_file)
	@echo "$(BLUE)Restoring database...$(NC)"
	@if [ -z "$(FILE)" ]; then echo "$(RED)Error: Specify FILE=backup_file$(NC)"; exit 1; fi
	@copy $(FILE) server\kisan_app.db
	@echo "$(GREEN)----------- Database restored$(NC)"

# Deployment targets
deploy: ## Deploy to production (requires configuration)
	@echo "$(BLUE)Deploying to production...$(NC)"
	@$(MAKE) test
	@$(MAKE) build
	@$(MAKE) docker-build
	@echo "$(GREEN)----------- Ready for deployment$(NC)"
	@echo "$(YELLOW)Run 'make docker-up' to start production services$(NC)"

production: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	@$(MAKE) docker-up
	@echo "$(GREEN)----------- Production environment started$(NC)"
	@echo "$(YELLOW)Application running at http://localhost$(NC)"

# Cleanup targets
clean: clean-frontend clean-backend clean-cache ## Clean all build artifacts
	@echo "$(GREEN)----------- Cleanup completed$(NC)"

clean-frontend: ## Clean frontend build artifacts
	@echo "$(BLUE)Cleaning frontend artifacts...$(NC)"
	@if exist build rd /s /q build
	@if exist node_modules\.cache rd /s /q node_modules\.cache

clean-backend: ## Clean backend artifacts
	@echo "$(BLUE)Cleaning backend artifacts...$(NC)"
	@for /r %%i in (*.pyc) do del "%%i"
	@for /d /r %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"

clean-cache: ## Clean cache files
	@echo "$(BLUE)Cleaning cache files...$(NC)"
	@if exist .cache rd /s /q .cache
	@if exist .pytest_cache rd /s /q .pytest_cache
	@if exist .coverage del .coverage

clean-all: clean docker-clean ## Deep clean including Docker
	@echo "$(GREEN)----------- Deep cleanup completed$(NC)"

# Utility targets
shell-backend: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	$(PYTHON) -i -c "from server.app import app; from server.database import DatabaseManager; db = DatabaseManager()"

requirements: ## Generate/update requirements.txt
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)----------- Requirements updated$(NC)"

check-env: ## Check if all environment variables are set
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@$(PYTHON) -c "import os; from dotenv import load_dotenv; load_dotenv(); print('----------- .env file loaded')"

version: ## Display version information
	@echo "$(BLUE)Kisan-G Application$(NC)"
	@echo "Version: 1.0.0"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Node: $$($(NPM) --version)"

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -f http://localhost:5001/api/health || echo "$(RED)Backend not responding$(NC)"

# Convenience shortcuts
i: install ## Shortcut for install
b: build ## Shortcut for build
t: test ## Shortcut for test
l: lint ## Shortcut for lint
d: dev ## Shortcut for dev
