# =============================================================================
# RAG Services Makefile
# =============================================================================

.PHONY: help rag-up rag-down rag-build rag-rebuild rag-logs rag-verify \
        rag-index rag-backup rag-restore rag-clean rag-status \
        haystack-shell lightrag-shell neo4j-browser postgres-shell \
        init-data-dirs

# Colors
COLOR_RESET = \033[0m
COLOR_BOLD = \033[1m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_RED = \033[31m
COLOR_CYAN = \033[36m

# Default target
.DEFAULT_GOAL := help

# Load environment variables
-include .env
export

help: ## Show this help message
	@echo "$(COLOR_BOLD)RAG Services - Docker Management$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_CYAN)Lifecycle:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)rag-up$(COLOR_RESET)          Start all RAG services"
	@echo "  $(COLOR_GREEN)rag-down$(COLOR_RESET)        Stop all services"
	@echo "  $(COLOR_GREEN)rag-build$(COLOR_RESET)       Build Docker images"
	@echo "  $(COLOR_GREEN)rag-rebuild$(COLOR_RESET)     Rebuild images (no cache)"
	@echo "  $(COLOR_GREEN)rag-restart$(COLOR_RESET)     Restart all services"
	@echo "  $(COLOR_GREEN)rag-status$(COLOR_RESET)      Show service status"
	@echo ""
	@echo "$(COLOR_CYAN)Monitoring:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)rag-logs$(COLOR_RESET)        Tail all service logs"
	@echo "  $(COLOR_GREEN)rag-logs-haystack$(COLOR_RESET) Tail Haystack logs"
	@echo "  $(COLOR_GREEN)rag-logs-lightrag$(COLOR_RESET) Tail LightRAG logs"
	@echo "  $(COLOR_GREEN)rag-verify$(COLOR_RESET)      Health check all services"
	@echo ""
	@echo "$(COLOR_CYAN)Data Management:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)rag-index$(COLOR_RESET)       Index framework documentation"
	@echo "  $(COLOR_GREEN)rag-index-ref$(COLOR_RESET)   Index only REF documents (Layer 0)"
	@echo "  $(COLOR_GREEN)rag-backup$(COLOR_RESET)      Backup all data"
	@echo "  $(COLOR_GREEN)rag-restore$(COLOR_RESET)     Restore from backup"
	@echo "  $(COLOR_GREEN)rag-clean$(COLOR_RESET)       Remove all data (DANGER)"
	@echo ""
	@echo "$(COLOR_CYAN)Interactive:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)haystack-shell$(COLOR_RESET)  Shell into Haystack container"
	@echo "  $(COLOR_GREEN)lightrag-shell$(COLOR_RESET)  Shell into LightRAG container"
	@echo "  $(COLOR_GREEN)postgres-shell$(COLOR_RESET)  PostgreSQL interactive shell"
	@echo "  $(COLOR_GREEN)neo4j-browser$(COLOR_RESET)   Show Neo4j Browser URL"
	@echo ""
	@echo "$(COLOR_CYAN)Setup:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)setup$(COLOR_RESET)           Initial setup (copy .env, create dirs)"
	@echo "  $(COLOR_GREEN)init-data-dirs$(COLOR_RESET)  Create tools/data directories in PROJECT_ROOT"
	@echo "  $(COLOR_GREEN)check-env$(COLOR_RESET)       Verify environment configuration"
	@echo ""
	@echo "$(COLOR_CYAN)Data Storage:$(COLOR_RESET)"
	@echo "  Data is stored in: \$${PROJECT_ROOT}/tools/data/"
	@echo "    - postgres/   PostgreSQL database"
	@echo "    - neo4j/      Neo4j graph database"
	@echo "    - haystack/   Haystack indexes"
	@echo "    - lightrag/   LightRAG data"
	@echo "    - backups/    Backup files"
	@echo ""

# =============================================================================
# Setup
# =============================================================================

setup: ## Initial setup
	@echo "$(COLOR_GREEN)Setting up RAG services...$(COLOR_RESET)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(COLOR_YELLOW)Created .env from .env.example$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)Please edit .env with:$(COLOR_RESET)"; \
		echo "  1. PROJECT_ROOT - Path to your project directory"; \
		echo "  2. OPENAI_API_KEY - Your OpenAI API key"; \
	else \
		echo ".env already exists"; \
	fi
	@mkdir -p tmp
	@echo ""
	@echo "$(COLOR_GREEN)Next steps:$(COLOR_RESET)"
	@echo "  1. Edit .env with your PROJECT_ROOT and API keys"
	@echo "  2. Run 'make init-data-dirs' to create data directories"
	@echo "  3. Run 'make rag-build' to build Docker images"
	@echo "  4. Run 'make rag-up' to start services"

init-data-dirs: check-env ## Create tools/data directories in PROJECT_ROOT
	@echo "$(COLOR_GREEN)Creating data directories in $(PROJECT_ROOT)/tools/data/...$(COLOR_RESET)"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/postgres"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/neo4j/data"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/neo4j/logs"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/haystack/data"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/haystack/pipelines"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/lightrag/data"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/lightrag/inputs"
	@mkdir -p "$(PROJECT_ROOT)/tools/data/backups"
	@echo "$(COLOR_GREEN)Data directories created:$(COLOR_RESET)"
	@ls -la "$(PROJECT_ROOT)/tools/data/"

check-env: ## Verify environment configuration
	@echo "$(COLOR_GREEN)Checking environment...$(COLOR_RESET)"
	@if [ ! -f .env ]; then \
		echo "$(COLOR_RED)ERROR: .env file not found. Run 'make setup' first.$(COLOR_RESET)"; \
		exit 1; \
	fi
	@if grep -q "/path/to/your/project" .env; then \
		echo "$(COLOR_RED)ERROR: PROJECT_ROOT not set in .env$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)Set PROJECT_ROOT to your project directory path$(COLOR_RESET)"; \
		exit 1; \
	fi
	@if grep -q "sk-your-openai-api-key-here" .env; then \
		echo "$(COLOR_RED)ERROR: OPENAI_API_KEY not set in .env$(COLOR_RESET)"; \
		exit 1; \
	fi
	@if [ ! -d "$(PROJECT_ROOT)/tools/data" ]; then \
		echo "$(COLOR_YELLOW)WARNING: Data directories not found. Run 'make init-data-dirs'$(COLOR_RESET)"; \
	fi
	@echo "$(COLOR_GREEN)Environment OK$(COLOR_RESET)"
	@echo "  PROJECT_ROOT: $(PROJECT_ROOT)"

# =============================================================================
# Lifecycle
# =============================================================================

rag-build: check-env init-data-dirs ## Build Docker images
	@echo "$(COLOR_GREEN)Building RAG Docker images...$(COLOR_RESET)"
	docker-compose build

rag-rebuild: check-env ## Rebuild images without cache
	@echo "$(COLOR_GREEN)Rebuilding RAG Docker images (no cache)...$(COLOR_RESET)"
	docker-compose build --no-cache

rag-up: check-env ## Start all RAG services
	@echo "$(COLOR_GREEN)Starting RAG services...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Data storage: $(PROJECT_ROOT)/tools/data/$(COLOR_RESET)"
	docker-compose up -d
	@echo ""
	@echo "$(COLOR_CYAN)Services starting. Check status with 'make rag-status'$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)View logs with 'make rag-logs'$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Service URLs:$(COLOR_RESET)"
	@echo "  Haystack API:    http://localhost:1416"
	@echo "  LightRAG API:    http://localhost:9621"
	@echo "  Neo4j Browser:   http://localhost:7474"
	@echo "  PostgreSQL:      localhost:5432"

rag-down: ## Stop all services
	@echo "$(COLOR_GREEN)Stopping RAG services...$(COLOR_RESET)"
	docker-compose down

rag-restart: ## Restart all services
	@echo "$(COLOR_GREEN)Restarting RAG services...$(COLOR_RESET)"
	docker-compose restart

rag-status: ## Show service status
	@echo "$(COLOR_GREEN)RAG Service Status:$(COLOR_RESET)"
	@docker-compose ps
	@echo ""
	@echo "$(COLOR_CYAN)Data storage: $(PROJECT_ROOT)/tools/data/$(COLOR_RESET)"

# =============================================================================
# Monitoring
# =============================================================================

rag-logs: ## Tail all service logs
	docker-compose logs -f

rag-logs-haystack: ## Tail Haystack logs
	docker-compose logs -f haystack

rag-logs-lightrag: ## Tail LightRAG logs
	docker-compose logs -f lightrag

rag-verify: ## Health check all services
	@echo "$(COLOR_GREEN)Checking service health...$(COLOR_RESET)"
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec -T postgres pg_isready -U raguser -d ragdb && \
		echo "  $(COLOR_GREEN)✓ Healthy$(COLOR_RESET)" || \
		echo "  $(COLOR_RED)✗ Unhealthy$(COLOR_RESET)"
	@echo ""
	@echo "Neo4j:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:7474 | grep -q "200" && \
		echo "  $(COLOR_GREEN)✓ Healthy$(COLOR_RESET)" || \
		echo "  $(COLOR_RED)✗ Unhealthy$(COLOR_RESET)"
	@echo ""
	@echo "Haystack:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:1416/health 2>/dev/null | grep -q "200" && \
		echo "  $(COLOR_GREEN)✓ Healthy$(COLOR_RESET)" || \
		echo "  $(COLOR_YELLOW)⚠ Not ready (may still be starting)$(COLOR_RESET)"
	@echo ""
	@echo "LightRAG:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:9621/health 2>/dev/null | grep -q "200" && \
		echo "  $(COLOR_GREEN)✓ Healthy$(COLOR_RESET)" || \
		echo "  $(COLOR_YELLOW)⚠ Not ready (may still be starting)$(COLOR_RESET)"
	@echo ""

# =============================================================================
# Data Management
# =============================================================================

rag-index: ## Index framework documentation
	@echo "$(COLOR_GREEN)Indexing framework documentation...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)This will index docs from ../ai_dev_ssd_flow/ (including 00_REF)$(COLOR_RESET)"
	python rag_tools/batch_indexer.py --source ../ai_dev_ssd_flow --verbose

rag-index-ref: ## Index only REF documents (Layer 0)
	@echo "$(COLOR_GREEN)Indexing reference documents (Layer 0)...$(COLOR_RESET)"
	python rag_tools/batch_indexer.py --source ../ai_dev_ssd_flow/00_REF --verbose

rag-index-project: check-env ## Index project documentation from PROJECT_ROOT
	@echo "$(COLOR_GREEN)Indexing project documentation from $(PROJECT_ROOT)...$(COLOR_RESET)"
	python rag_tools/batch_indexer.py --source "$(PROJECT_ROOT)/docs" --verbose

rag-backup: check-env ## Backup all data
	@echo "$(COLOR_GREEN)Backing up RAG data...$(COLOR_RESET)"
	@BACKUP_DIR="$(PROJECT_ROOT)/tools/data/backups/backup_$$(date +%Y%m%d_%H%M%S)"; \
	mkdir -p "$$BACKUP_DIR"; \
	echo "Backing up PostgreSQL..."; \
	docker-compose exec -T postgres pg_dump -U raguser ragdb > "$$BACKUP_DIR/postgres.sql"; \
	echo "Backing up Neo4j..."; \
	docker-compose exec -T neo4j neo4j-admin database dump neo4j --to-stdout > "$$BACKUP_DIR/neo4j.dump" 2>/dev/null || echo "Neo4j backup requires enterprise edition"; \
	echo "$(COLOR_GREEN)Backup complete: $$BACKUP_DIR$(COLOR_RESET)"

rag-restore: check-env ## Restore from backup
	@echo "$(COLOR_YELLOW)Available backups:$(COLOR_RESET)"
	@ls -la "$(PROJECT_ROOT)/tools/data/backups/" 2>/dev/null || echo "No backups found"
	@echo ""
	@echo "To restore, run:"
	@echo "  cat $(PROJECT_ROOT)/tools/data/backups/BACKUP_DIR/postgres.sql | docker-compose exec -T postgres psql -U raguser ragdb"

rag-clean: check-env ## Remove all data (DANGER)
	@echo "$(COLOR_RED)WARNING: This will delete all RAG data in $(PROJECT_ROOT)/tools/data/!$(COLOR_RESET)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down; \
		rm -rf "$(PROJECT_ROOT)/tools/data/postgres"/*; \
		rm -rf "$(PROJECT_ROOT)/tools/data/neo4j"/*; \
		rm -rf "$(PROJECT_ROOT)/tools/data/haystack"/*; \
		rm -rf "$(PROJECT_ROOT)/tools/data/lightrag"/*; \
		echo "$(COLOR_GREEN)All data removed$(COLOR_RESET)"; \
	else \
		echo "Cancelled"; \
	fi

# =============================================================================
# Interactive
# =============================================================================

haystack-shell: ## Shell into Haystack container
	docker-compose exec haystack /bin/bash

lightrag-shell: ## Shell into LightRAG container
	docker-compose exec lightrag /bin/bash

postgres-shell: ## PostgreSQL interactive shell
	docker-compose exec postgres psql -U raguser ragdb

neo4j-browser: ## Show Neo4j Browser URL
	@echo "$(COLOR_GREEN)Neo4j Browser:$(COLOR_RESET) http://localhost:7474"
	@echo "$(COLOR_CYAN)Username: neo4j$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Password: (see NEO4J_PASSWORD in .env)$(COLOR_RESET)"

# =============================================================================
# Development
# =============================================================================

rag-eval: ## Run RAGAS evaluation
	@echo "$(COLOR_GREEN)Running RAG evaluation...$(COLOR_RESET)"
	python haystack/scripts/evaluate.py

test: ## Run tests
	@echo "$(COLOR_GREEN)Running tests...$(COLOR_RESET)"
	pytest haystack/tests/ lightrag/tests/ -v

lint: ## Run linters
	@echo "$(COLOR_GREEN)Running linters...$(COLOR_RESET)"
	ruff check haystack/src/ lightrag/src/ rag_tools/
	black --check haystack/src/ lightrag/src/ rag_tools/
