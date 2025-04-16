# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

.DEFAULT_GOAL := help

.PHONY: test coverage clean build install lint

# The help target displays a help message that includes the avialable targets
# in this `Makefile`.  It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  build      - Builds the iap application binary"
	@echo "  clean      - Cleans the development environment"
	@echo "  coverage   - Run test coverage report"
	@echo "  install    - Install application dependencies"
	@echo "  lint       - Run analysis on source files"
	@echo "  test       - Run test suite"
	@echo ""

test:
	uv run pytest tests

coverage:
	uv run pytest --cov=ipsdk --cov-report=term --cov-report=html tests/

build:
	python -m build

install:
	uv pip install "ipctl[dev]"

lint:
	uv run ruff check ipsdk
	uv run ruff check tests

clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info
