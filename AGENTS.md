# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Itential Python SDK

## Development Commands

This project uses `uv` as the Python package manager and build tool. Key commands:

- **Install dependencies**: `uv sync` (creates virtual environment and installs dependencies)
- **Run tests**: `uv run pytest tests` or `make test`
- **Run single test**: `uv run pytest tests/test_<module>.py::<test_function>`
- **Run tests with coverage**: `uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/` or `make coverage`
- **Run tests with coverage check**: `make coverage-check` (enforces 95% minimum coverage, fails if below threshold)
- **Lint code**: `uv run ruff check src/ipsdk` and `uv run ruff check tests` or `make lint`
- **Format code**: `uv run ruff format src/ipsdk tests` or `make format` (automatic code formatting)
- **Auto-fix linting issues**: `uv run ruff check --fix src/ipsdk tests` or `make ruff-fix` (auto-fix where possible)
- **Type checking**: `uv run mypy src/ipsdk` (mypy is in dev dependencies)
- **Security analysis**: `uv run bandit -r src/ipsdk --configfile pyproject.toml` or `make security` (scans for security vulnerabilities)
- **Clean build artifacts**: `make clean`
- **Run premerge checks**: `make premerge` (runs clean, lint, security, and coverage-check with 95% threshold)
- **Run specific test module**: `uv run pytest tests/test_<module>.py`
- **Pre-commit hooks**: `uv run pre-commit install` (install git hooks), `uv run pre-commit run --all-files` (run on all files)
- **Generate changelog**: `make changelog` (generates full CHANGELOG.md), `make changelog-unreleased` (shows unreleased changes)
- **git-cliff**: Uses conventional commits to generate changelog automatically on version tags

## Project Architecture

The Itential Python SDK provides HTTP client implementations for connecting to Itential Platform and Itential Automation Gateway 4.x.

### Project Details

- **License**: GPL-3.0-or-later
- **Python Support**: >=3.8 (tested on 3.10, 3.11, 3.12, 3.13)
- **Status**: Beta
- **Primary Dependency**: httpx>=0.28.1
- **Build System**: Hatchling with uv-dynamic-versioning
- **Version**: Dynamic versioning from git tags using PEP440 style

### Core Structure

- **Factory Functions**: Entry points in `__init__.py`
  - `platform_factory()` - Creates connections to Itential Platform
  - `gateway_factory()` - Creates connections to Itential Automation Gateway
  - Exports: `gateway_factory`, `logger`, `platform_factory`

- **Connection Layer** (`connection.py`):
  - `ConnectionBase` - Abstract base class with shared functionality
  - `Connection` - Synchronous HTTP client using httpx
  - `AsyncConnection` - Asynchronous HTTP client using httpx.AsyncClient
  - `Request` - Wrapper class for HTTP request data (method, path, params, headers, json)
  - `Response` - Wrapper class for HTTP response data with JSON utilities
  - Both support GET, POST, PUT, DELETE, PATCH methods

- **Authentication**:
  - Platform (`platform.py`) supports both OAuth (client credentials) and basic auth
  - Gateway (`gateway.py`) supports basic auth only
  - Auth mixins handle automatic authentication on first request

- **Base URLs**:
  - Platform: `<host>` (direct)
  - Gateway: `<host>/api/v2.0`

- **Core Modules**:
  - `connection.py` - HTTP client implementations and request/response wrappers
  - `exceptions.py` - Centralized exception classes for error handling
  - `gateway.py` - Itential Automation Gateway client with basic auth
  - `jsonutils.py` - JSON serialization/deserialization utilities
  - `logging.py` - Comprehensive logging system with file/console handlers, custom FATAL level (90), and httpx/httpcore control
  - `metadata.py` - Package metadata and dynamic version information from importlib
  - `platform.py` - Itential Platform client with OAuth and basic auth support

### Key Features

- Automatic authentication on first API call
- Support for both sync and async operations (controlled by `want_async` parameter)
- Configurable TLS, certificate verification, timeouts
- **Comprehensive Logging System**:
  - Multiple log levels including custom FATAL (90) level
  - Convenience functions: `debug()`, `info()`, `warning()`, `error()`, `critical()`, `fatal()`, `exception()`
  - File logging with automatic directory creation and custom formatting
  - Console output control (stdout/stderr switching)
  - httpx/httpcore logging control via `propagate` parameter
  - Centralized configuration via `set_level()` and `configure_file_logging()`
- JSON request/response handling with automatic Content-Type headers


### Code Quality and Linting

- **Ruff Configuration**: Comprehensive linting and formatting rules configured in `pyproject.toml`
  - Includes 30+ rule sets: pycodestyle (E,W), Pyflakes (F), pyupgrade (UP), flake8-bugbear (B), isort (I), pylint (PL), security checks (S), annotations (ANN), async (ASYNC), and many more
  - Line length set to 88 characters (Black-compatible)
  - Target Python 3.8+ compatibility
  - Per-file ignores configured for different modules (tests/, connection.py, platform.py, gateway.py, logging.py, exceptions.py)
  - Auto-fixable rules enabled for most issues
  - Double quotes for strings, space indentation, magic trailing comma support
- **Pre-commit Hooks**: Configured in `.pre-commit-config.yaml` for automatic code quality checks
  - Pre-commit hooks v4.6.0 with basic file checks (trailing whitespace, EOF fixer, YAML/TOML validation, large files, merge conflicts, debug statements)
  - Ruff pre-commit v0.8.4 with linting (--fix) and formatting
  - MyPy v1.13.0 with httpx dependencies and --ignore-missing-imports
- **Make Targets**:
  - `make format` - Format code with ruff
  - `make ruff-fix` - Auto-fix linting issues
  - `make lint` - Run full linting checks

### Development Dependencies

Core dev dependencies in `dependency-groups.dev`:
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Linting/Formatting**: ruff, mypy
- **Utilities**: q (debugging), coverage, build, pre-commit

### Testing

- Uses pytest with async support (`pytest-asyncio`)
- Test files in `tests/` directory cover all main components: connection, exceptions, gateway, jsonutils, logging, platform
- Coverage reporting available via pytest-cov with HTML and terminal output
- **Coverage requirement**: Minimum 95% test coverage enforced in CI/CD pipeline
- Tests include extensive per-file ignore rules in ruff config to allow test-specific patterns
- The premerge pipeline automatically fails if coverage drops below 95%

#### Logging Module Testing

The `tests/test_logging.py` file provides comprehensive testing coverage for the logging system with **38 test cases**:

- **Constants and Levels**: Verification of all logging constants and custom FATAL level (90) registration
- **Core Functionality**: Testing of main `log()` function and all convenience functions (`debug`, `info`, `warning`, `error`, `critical`, `fatal`, `exception`)
- **Configuration Functions**: Complete testing of `set_level()`, `configure_file_logging()`, and `get_logger()`
- **File Handler Management**: Tests for `add_file_handler()`, `remove_file_handlers()` with parent directory creation
- **Console Handler Control**: Testing of `set_console_output()`, `add_stdout_handler()`, `add_stderr_handler()`
- **Integration Tests**: Real logging output verification and file logging functionality
- **Error Handling**: Exception logging, fatal function with system exit, and validation error testing
- **Edge Cases**: Handler cleanup, custom formatting, propagation control, and initialization testing

#### Python Version Testing Matrix

The SDK officially supports Python 3.8+ but is tested on the following versions:

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.10           | ✅ Tested | Minimum recommended version |
| 3.11           | ✅ Tested | Full support |
| 3.12           | ✅ Tested | Full support |
| 3.13           | ✅ Tested | Latest stable release |
| 3.14           | 🔄 Beta | Development/preview testing |

**Testing Commands by Version:**
- `uv run --python 3.10 pytest tests` - Test with Python 3.10
- `uv run --python 3.11 pytest tests` - Test with Python 3.11
- `uv run --python 3.12 pytest tests` - Test with Python 3.12
- `uv run --python 3.13 pytest tests` - Test with Python 3.13

**Matrix Testing:**
```bash
# Test all supported versions locally
for version in 3.10 3.11 3.12 3.13; do
    echo "Testing Python $version"
    uv run --python $version pytest tests
done
```

**GitHub Actions Matrix:**
The `.github/workflows/premerge.yaml` workflow runs tests against all supported Python versions:
- Uses `strategy.matrix` with Python versions 3.10, 3.11, 3.12, 3.13
- Sets `fail-fast: false` to run all versions even if one fails
- Each version runs the full `make premerge` target (clean, lint, test)

### Key Implementation Details

- **Request/Response Wrappers**: The SDK provides `Request` and `Response` wrapper classes that encapsulate HTTP request/response data with additional functionality beyond raw httpx objects
- **Advanced Logging System**: Full-featured logging implementation with comprehensive functionality:
  - **Custom Levels**: FATAL level (90) in addition to standard levels (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
  - **Multiple Handlers**: File handlers, console handlers (stdout/stderr), with automatic cleanup
  - **Configuration Functions**: 
    - `set_level(lvl, *, propagate=False)` - Set logging level with optional httpx/httpcore control
    - `configure_file_logging(file_path, level=INFO, *, propagate=False, format_string=None)` - One-call setup
    - `add_file_handler()`, `remove_file_handlers()` - File logging management
    - `set_console_output()`, `add_stdout_handler()`, `add_stderr_handler()` - Console control
  - **Convenience Functions**: `debug()`, `info()`, `warning()`, `error()`, `critical()`, `fatal()`, `exception()`
  - **Automatic Features**: Directory creation, custom formatting, propagation control, handler cleanup
  - **Google-style Documentation**: All functions have comprehensive docstrings with Args/Returns/Raises sections
- **Exception Handling**: Centralized exception classes in `exceptions.py` for consistent error handling across the SDK
- **JSON Utilities**: Dedicated `jsonutils.py` module for JSON serialization/deserialization operations
- **Metadata Management**: Version and package metadata handled via `metadata.py` with dynamic versioning from git using importlib.metadata
- **Build System**: Uses Hatchling with uv-dynamic-versioning for PEP440-style git tag-based versioning with bump support and 0.0.0 fallback

### Documentation Standards

- Always put verbose documentation for all methods and functions
- Docstrings should use google style documentation strings
- All docstrings must include Args:, Returns:, Raises:
- Raises must only document exceptions returned by the function or method

The SDK abstracts away the complexity of authentication and HTTP client management, providing simple factory functions that return ready-to-use client objects for making API calls.
