# AI Dev Flow Framework - Makefile
# Version: 1.0
# Last Updated: 2026-01-19

.PHONY: help validate docs autopilot test lint clean install docker-build docker-run format watch

# Color output for better readability
COLOR_RESET = \033[0m
COLOR_BOLD = \033[1m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_RED = \033[31m

help: ## Show this help message
	@echo "$(COLOR_BOLD)Available targets:$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)validate      $(COLOR_RESET)  Run all framework validators"
	@echo "$(COLOR_GREEN)docs          $(COLOR_RESET)  Generate MVP documentation"
	@echo "$(COLOR_GREEN)autopilot     $(COLOR_RESET)  Run autopilot with defaults"
	@echo "$(COLOR_GREEN)test          $(COLOR_RESET)  Run autopilot test suite"
	@echo "$(COLOR_GREEN)lint          $(COLOR_RESET)  Run Python linters"
	@echo "$(COLOR_GREEN)format         $(COLOR_RESET)  Format Python code"
	@echo "$(COLOR_GREEN)clean         $(COLOR_RESET)  Remove generated files and reports"
	@echo "$(COLOR_GREEN)install        $(COLOR_RESET)  Install Python dependencies"
	@echo "$(COLOR_GREEN)docker-build    $(COLOR_RESET)  Build Docker images"
	@echo "$(COLOR_GREEN)docker-run     $(COLOR_RESET)  Run Docker containers"
	@echo "$(COLOR_GREEN)watch         $(COLOR_RESET)  Watch for file changes (dev mode)"
	@echo ""
	@echo "$(COLOR_BOLD)Validation targets:$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  validate-brd  $(COLOR_RESET)  Validate BRD layer"
	@echo "$(COLOR_GREEN)  validate-prd  $(COLOR_RESET)  Validate PRD layer"
	@echo "$(COLOR_GREEN)  validate-ears  $(COLOR_RESET)  Validate EARS layer"
	@echo "$(COLOR_GREEN)  validate-bdd  $(COLOR_RESET)  Validate BDD layer"
	@echo "$(COLOR_GREEN)  validate-adr  $(COLOR_RESET)  Validate ADR layer"
	@echo "$(COLOR_GREEN)  validate-sys  $(COLOR_RESET)  Validate SYS layer"
	@echo "$(COLOR_GREEN)  validate-req  $(COLOR_RESET)  Validate REQ layer"
	@echo "$(COLOR_GREEN)  validate-ctr  $(COLOR_RESET)  Validate CTR layer"
	@echo "$(COLOR_GREEN)  validate-spec  $(COLOR_RESET)  Validate SPEC layer"
	@echo "$(COLOR_GREEN)  validate-tasks $(COLOR_RESET)  Validate TASKS layer"
	@echo ""
	@echo "$(COLOR_BOLD)Documentation targets:$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)docs-full      $(COLOR_RESET)  Generate full MVP documentation (BRD→TASKS)"
	@echo "$(COLOR_GREEN)docs-prd      $(COLOR_RESET)  Start from PRD (generate PRD→TASKS)"
	@echo "$(COLOR_GREEN)docs-ears     $(COLOR_RESET)  Start from EARS (generate EARS→TASKS)"
	@echo ""

validate: ## Run all validators
	@echo "$(COLOR_BOLD)Running framework validation...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--all \
		--report markdown

validate-brd: ## Validate BRD layer
	@echo "$(COLOR_GREEN)Validating BRD layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer BRD \
		--report markdown

validate-prd: ## Validate PRD layer
	@echo "$(COLOR_GREEN)Validating PRD layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer PRD \
		--report markdown

validate-ears: ## Validate EARS layer
	@echo "$(COLOR_GREEN)Validating EARS layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer EARS \
		--report markdown

validate-bdd: ## Validate BDD layer
	@echo "$(COLOR_GREEN)Validating BDD layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer BDD \
		--report markdown

validate-adr: ## Validate ADR layer
	@echo "$(COLOR_GREEN)Validating ADR layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer ADR \
		--report markdown

validate-sys: ## Validate SYS layer
	@echo "$(COLOR_GREEN)Validating SYS layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer SYS \
		--report markdown

validate-req: ## Validate REQ layer
	@echo "$(COLOR_GREEN)Validating REQ layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer REQ \
		--report markdown

validate-ctr: ## Validate CTR layer
	@echo "$(COLOR_GREEN)Validating CTR layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer CTR \
		--report markdown

validate-spec: ## Validate SPEC layer
	@echo "$(COLOR_GREEN)Validating SPEC layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer SPEC \
		--report markdown

validate-tasks: ## Validate TASKS layer
	@echo "$(COLOR_GREEN)Validating TASKS layer...$(COLOR_RESET)"
	python3 ai_dev_flow/scripts/validate_all.py \
		ai_dev_flow \
		--layer TASKS \
		--report markdown

docs: ## Generate MVP documentation
	@echo "$(COLOR_GREEN)Generating MVP documentation...$(COLOR_RESET)"
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--intent "My MVP" \
		--slug my_mvp \
		--up-to TASKS \
		--auto-fix \
		--report markdown

docs-full: ## Generate full MVP documentation (BRD→TASKS)
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--intent "My MVP" \
		--slug my_mvp \
		--up-to TASKS \
		--auto-fix \
		--report markdown

docs-prd: ## Start from PRD (PRD→TASKS)
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--from-layer PRD \
		--up-to TASKS \
		--auto-fix \
		--report markdown

docs-ears: ## Start from EARS (EARS→TASKS)
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--from-layer EARS \
		--up-to TASKS \
		--auto-fix \
		--report markdown

autopilot: ## Run autopilot with defaults
	@echo "$(COLOR_GREEN)Running autopilot with MVP profile...$(COLOR_RESET)"
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--intent "My MVP" \
		--slug my_mvp \
		--profile mvp \
		--auto-fix \
		--report markdown

autopilot-strict: ## Run autopilot with strict validation
	@echo "$(COLOR_GREEN)Running autopilot with strict profile...$(COLOR_RESET)"
	python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
		--root ai_dev_flow \
		--intent "My MVP" \
		--slug my_mvp \
		--profile strict \
		--strict \
		--auto-fix \
		--report markdown

test: ## Run autopilot test suite
	@echo "$(COLOR_GREEN)Running autopilot tests...$(COLOR_RESET)"
	python3 -m pytest ai_dev_flow/AUTOPILOT/tests/ -v

lint: ## Run Python linters
	@echo "$(COLOR_GREEN)Running Python linters...$(COLOR_RESET)"
	python3 -m ruff check ai_dev_flow/AUTOPILOT/scripts/ ai_dev_flow/scripts/
	python3 -m mypy ai_dev_flow/AUTOPILOT/scripts/

format: ## Format Python code
	@echo "$(COLOR_GREEN)Formatting Python code...$(COLOR_RESET)"
	black ai_dev_flow/AUTOPILOT/scripts/
	isort ai_dev_flow/AUTOPILOT/scripts/

clean: ## Remove generated files and reports
	@echo "$(COLOR_GREEN)Cleaning generated files...$(COLOR_RESET)"
	find ai_dev_flow/AUTOPILOT/work_plans -name "*.md" -delete 2>/dev/null || true
	find ai_dev_flow/AUTOPILOT/work_plans -name "*.json" -delete 2>/dev/null || true

install: ## Install Python dependencies
	@echo "$(COLOR_GREEN)Installing Python dependencies...$(COLOR_RESET)"
	pip install --quiet --upgrade pip
	pip install --quiet -r ai_dev_flow/scripts/requirements.txt
	pip install --quiet -r ai_dev_flow/AUTOPILOT/scripts/requirements.txt

docker-build: ## Build Docker images
	@echo "$(COLOR_GREEN)Building Docker images...$(COLOR_RESET)"
	docker build -t ai_dev_flow_autopilot .

docker-run: ## Run Docker containers
	@echo "$(COLOR_GREEN)Running Docker containers...$(COLOR_RESET)"
	docker run --rm -v "$(PWD):/opt/data/docs_flow_framework" ai_dev_flow_autopilot

watch: ## Watch for file changes and auto-reload config
	@echo "$(COLOR_GREEN)Watching for file changes...$(COLOR_RESET)"
	python3 ai_dev_flow/AUTOPILOT/scripts/dev_mode.py --watch --root ai_dev_flow

.DEFAULT_GOAL := help
