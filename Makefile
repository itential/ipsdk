# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# ==============================================================================
# ipsdk — HTTP client SDK for Itential Platform and Automation Gateway
# ==============================================================================
# Usage:
#   make              Show available targets
#   make test         Run unit tests
#   make ci           Run all checks (use before committing)
#
# Dependencies: uv (https://github.com/astral-sh/uv)
# ==============================================================================

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

UV      ?= uv
SRC     := src/ipsdk
TESTS   := tests
SCRIPTS := scripts

# ------------------------------------------------------------------------------
# Core
# ------------------------------------------------------------------------------

.PHONY: test coverage build

test: ## Run unit tests
	$(UV) run pytest $(TESTS) -v

coverage: ## Run tests with coverage report (enforces 100%)
	$(UV) run pytest \
		--cov=$(SRC) \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=100 \
		$(TESTS)/

build: ## Build distribution packages (wheel + sdist)
	$(UV) build

# ------------------------------------------------------------------------------
# Quality checks
# ------------------------------------------------------------------------------

.PHONY: lint format format-check ruff-fix security license license-fix notice-check

lint: ## Lint with ruff
	$(UV) run ruff check $(SRC) $(TESTS)

format: ## Format source files with ruff
	$(UV) run ruff format $(SRC) $(TESTS)

format-check: ## Check formatting without modifying files
	$(UV) run ruff format --check $(SRC) $(TESTS)

ruff-fix: ## Auto-fix ruff lint issues
	$(UV) run ruff check --fix $(SRC) $(TESTS)

security: ## Run bandit security analysis
	$(UV) run bandit -r $(SRC) --configfile pyproject.toml

license: ## Check all Python files for license headers
	$(UV) run python $(SCRIPTS)/check_license_headers.py

license-fix: ## Add missing license headers to Python files
	$(UV) run python $(SCRIPTS)/check_license_headers.py --fix

notice-check: ## Verify NOTICE file lists all packages in uv.lock
	@echo "Packages in uv.lock not mentioned in NOTICE:"
	@grep -E '^name = "' uv.lock | sed 's/name = "\(.*\)"/\1/' | \
		grep -v '^ipsdk$$' | \
		while read pkg; do \
			normalized=$$(echo "$$pkg" | tr '-' '.'); \
			if ! grep -qi "$$pkg" NOTICE && ! grep -qi "$$normalized" NOTICE; then \
				echo "  MISSING: $$pkg"; \
			fi \
		done
	@echo "Done."

# ------------------------------------------------------------------------------
# CI
# ------------------------------------------------------------------------------

.PHONY: ci

ci: clean lint format-check security license tox ## Run all checks (required before committing)

# ------------------------------------------------------------------------------
# Tox (multi-version)
# ------------------------------------------------------------------------------

.PHONY: tox tox-py310 tox-py311 tox-py312 tox-py313 tox-py314
.PHONY: tox-coverage tox-lint tox-format tox-security tox-ci tox-list

tox: ## Run tests across all Python versions (3.10-3.14)
	$(UV) run tox

tox-py310: ## Run tests with Python 3.10
	$(UV) run tox -e py310

tox-py311: ## Run tests with Python 3.11
	$(UV) run tox -e py311

tox-py312: ## Run tests with Python 3.12
	$(UV) run tox -e py312

tox-py313: ## Run tests with Python 3.13
	$(UV) run tox -e py313

tox-py314: ## Run tests with Python 3.14
	$(UV) run tox -e py314

tox-coverage: ## Run coverage report via tox
	$(UV) run tox -e coverage

tox-lint: ## Run lint via tox
	$(UV) run tox -e lint

tox-format: ## Run format via tox
	$(UV) run tox -e format

tox-security: ## Run security scan via tox
	$(UV) run tox -e security

tox-ci: ## Run all CI checks via tox
	$(UV) run tox -e ci

tox-list: ## List all available tox environments
	$(UV) run tox list

# ------------------------------------------------------------------------------
# Housekeeping
# ------------------------------------------------------------------------------

.PHONY: clean

clean: ## Remove build artifacts and caches
	@rm -rf .pytest_cache .ruff_cache coverage.* htmlcov dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

.PHONY: help

help: ## Show available targets
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_/-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' \
		| sort
	@echo ""
