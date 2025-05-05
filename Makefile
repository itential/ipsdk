# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

.DEFAULT_GOAL := help

.PHONY: test coverage clean lint

# The help target displays a help message that includes the avialable targets
# in this `Makefile`.  It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  clean      - Cleans the development environment"
	@echo "  coverage   - Run test coverage report"
	@echo "  lint       - Run analysis on source files"
	@echo "  premerge   - Run the permerge tests locallly"
	@echo "  test       - Run test suite"
	@echo ""

# The test target will invoke the unit tests using pytest.   This target
# requires uv to be installed and the environment created.
test:
	uv run pytest tests

# The coverage target will invoke pytest with coverage support.  It will
# display a summary of the unit test coverage as well as output the coverage
# data report
coverage:
	uv run pytest --cov=ipsdk --cov-report=term --cov-report=html tests/

# The lint target invokes ruff to run the linter against both the library
# and test code.   This target is invoked in the premerge pipeline.
lint:
	uv run ruff check ipsdk
	uv run ruff check tests

# The clean target will remove build and dev artififacts that are not 
# part of the application and get created by other targets.
clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info

# The premerge target will run the permerge tests locally.  This is
# the same target that is invoked in the permerge pipeline.
premerge: clean lint test
