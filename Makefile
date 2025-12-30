# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

.DEFAULT_GOAL := help

.PHONY: test coverage clean lint format ruff-fix security license license-fix tox \
		tox-py310 tox-py311 tox-py312 tox-py313 tox-coverage tox-lint \
		tox-format tox-security tox-premerge tox-list

# The help target displays a help message that includes the avialable targets
# in this `Makefile`.  It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  clean           - Cleans the development environment"
	@echo "  coverage        - Run test coverage report"
	@echo "  format          - Format source files with ruff"
	@echo "  license         - Check all Python files for proper license headers"
	@echo "  license-fix     - Automatically add missing license headers to Python files"
	@echo "  lint            - Run analysis on source files"
	@echo "  premerge        - Run the premerge tests locally"
	@echo "  ruff-fix        - Run ruff with --fix to auto-fix issues"
	@echo "  security        - Run security analysis using bandit"
	@echo "  test            - Run test suite"
	@echo ""
	@echo "Tox targets:"
	@echo "  tox            - Run tests across all Python versions (3.10-3.13)"
	@echo "  tox-py310      - Run tests with Python 3.10"
	@echo "  tox-py311      - Run tests with Python 3.11"
	@echo "  tox-py312      - Run tests with Python 3.12"
	@echo "  tox-py313      - Run tests with Python 3.13"
	@echo "  tox-coverage   - Run tests with coverage report using tox"
	@echo "  tox-lint       - Run linting checks using tox"
	@echo "  tox-format     - Format code using tox"
	@echo "  tox-security   - Run security analysis using tox"
	@echo "  tox-premerge   - Run all premerge checks using tox"
	@echo "  tox-list       - List all available tox environments"
	@echo ""

# The test target will invoke the unit tests using pytest.   This target
# requires uv to be installed and the environment created.
test:
	uv run pytest tests -v -s

# The coverage target will invoke pytest with coverage support.  It will
# display a summary of the unit test coverage as well as output the coverage
# data report
coverage:
	uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/

# The lint target invokes ruff to run the linter against both the library
# and test code.   This target is invoked in the premerge pipeline.
lint:
	uv run ruff check src/ipsdk
	uv run ruff check tests

# The security target invokes bandit to run security analysis on the
# source code.  It scans for common security vulnerabilities.
security:
	uv run bandit -r src/ipsdk --configfile pyproject.toml

# The license target verifies that all Python files contain the
# proper license header.  This target is invoked in the premerge pipeline.
license:
	uv run python scripts/check_license_headers.py

# The license-fix target automatically adds missing license headers to
# all Python files in the project.
license-fix:
	uv run python scripts/check_license_headers.py --fix

# The clean target will remove build and dev artififacts that are not
# part of the application and get created by other targets.
clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# The format target will format source files using ruff
format:
	uv run ruff format src/ipsdk tests

# The ruff-fix target will run ruff with --fix to automatically fix
# fixable issues in the source code
ruff-fix:
	uv run ruff check --fix src/ipsdk
	uv run ruff check --fix tests

# The premerge target will run the permerge tests locally.  This is
# the same target that is invoked in the permerge pipeline.
premerge: clean lint security license test

# The tox target will run tests across all supported Python versions
# (3.10, 3.11, 3.12, 3.13) using tox with uv integration.
tox:
	uv run tox

# The tox-py310 target will run tests specifically with Python 3.10
tox-py310:
	uv run tox -e py310

# The tox-py311 target will run tests specifically with Python 3.11
tox-py311:
	uv run tox -e py311

# The tox-py312 target will run tests specifically with Python 3.12
tox-py312:
	uv run tox -e py312

# The tox-py313 target will run tests specifically with Python 3.13
tox-py313:
	uv run tox -e py313

# The tox-coverage target will run tests with coverage report using tox
tox-coverage:
	uv run tox -e coverage

# The tox-lint target will run linting checks using tox
tox-lint:
	uv run tox -e lint

# The tox-format target will format code using tox
tox-format:
	uv run tox -e format

# The tox-security target will run security analysis using tox
tox-security:
	uv run tox -e security

# The tox-premerge target will run all premerge checks using tox
tox-premerge:
	uv run tox -e premerge

# The tox-list target will list all available tox environments
tox-list:
	uv run tox list
