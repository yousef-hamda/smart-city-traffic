# Smart City Traffic Optimization Platform — developer entrypoints.
# Run `make help` for a description of every target.

COMPOSE      := docker compose
COMPOSE_DEV  := $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

.DEFAULT_GOAL := help

.PHONY: help dev dev-infra down test lint seed sim sim-camera sumo trino superset \
        chaos k8s-up k8s-down build scan models clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

dev: ## Start the full platform (infra + all services) with hot reload
	$(COMPOSE_DEV) --profile apps up -d --build
	@echo "→ Frontend:        http://localhost:3000"
	@echo "→ API Gateway:     http://localhost:8080/docs"
	@echo "→ Developer Portal http://localhost:3001"

dev-infra: ## Start only the data/streaming infrastructure
	$(COMPOSE) --profile infra up -d

down: ## Stop everything (volumes preserved)
	$(COMPOSE) --profile apps --profile infra --profile sim down

test: ## Run every service's test suite
	pnpm -r --if-present test
	@for svc in vision-service ml-prediction rl-optimizer federated-coordinator \
		ai-assistant voice-gateway sensor-simulator camera-simulator; do \
		( cd apps/$$svc && [ -f pyproject.toml ] && python -m pytest -q ) || exit 1; \
	done
	cd apps/sensor-ingestion && ./mvnw -q test

lint: ## Lint + typecheck all workspaces
	pnpm -r --if-present lint
	pnpm -r --if-present typecheck
	@for svc in vision-service ml-prediction rl-optimizer federated-coordinator \
		ai-assistant voice-gateway sensor-simulator camera-simulator; do \
		( cd apps/$$svc && ruff check src && mypy src ) || exit 1; \
	done

seed: ## Seed Postgres (segments, sensors, cameras) and the Neo4j road graph
	python3 scripts/seed/seed_postgres.py
	python3 scripts/seed/seed_neo4j.py

sim: ## Run the sensor simulator against the local stack
	$(COMPOSE) --profile sim up -d sensor-simulator

sim-camera: ## Run the camera simulator against the local stack
	$(COMPOSE) --profile sim up -d camera-simulator

sumo: ## Launch the SUMO RL training environment (requires SUMO installed)
	cd apps/rl-optimizer && python -m rl_optimizer.train --algo dqn

trino: ## Open a Trino shell against the data lake
	$(COMPOSE) exec trino trino --catalog iceberg --schema raw

superset: ## Start Superset BI (analytics profile)
	$(COMPOSE) --profile analytics up -d superset

chaos: ## Apply Litmus chaos experiments to the local cluster
	kubectl apply -f infra/litmus/

k8s-up: ## Install the Helm chart into the current kube context
	helm upgrade --install smart-city infra/helm/smart-city -n smart-city --create-namespace

k8s-down: ## Uninstall the Helm release
	helm uninstall smart-city -n smart-city

build: ## Build all service images
	$(COMPOSE) --profile apps --profile sim build

scan: ## Trivy-scan all built images
	bash scripts/security/trivy-scan-all.sh

models: ## Download / regenerate pre-trained model artifacts
	bash scripts/ml/fetch-models.sh

clean: ## Remove containers, volumes, build caches
	$(COMPOSE) --profile apps --profile infra --profile sim down -v
	pnpm -r --if-present clean || true
