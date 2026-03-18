# CLAUDE.md

## What This Is

HTTP client SDK for Itential Platform and Automation Gateway 4.x. Provides factory-based sync/async clients with lazy authentication, configurable TTL-based re-auth, comprehensive logging with PII redaction, and a custom exception hierarchy. The only runtime dependency is httpx.

**Current**: v0.8.0 | Python 3.10–3.14 | GPL-3.0-or-later

## Architecture

Factory functions (`platform_factory`, `gateway_factory`) are the sole public entry points. They construct client objects by composing auth mixins with HTTP base classes at runtime using `type()`. At type-check time (via `TYPE_CHECKING`), explicit class definitions are used instead so mypy and IDEs see proper types.

```
platform_factory() → Platform (AuthMixin + Connection)
                   → AsyncPlatform (AsyncAuthMixin + AsyncConnection)

gateway_factory()  → Gateway (AuthMixin + Connection)
                   → AsyncGateway (AsyncAuthMixin + AsyncConnection)
```

Authentication is lazy: the first `_send_request()` call acquires a `threading.Lock` (sync) or `asyncio.Lock` (async), checks `self.authenticated`, and calls `authenticate()` if needed. A double-checked locking pattern prevents races. TTL-based re-auth (`ttl > 0`) resets `authenticated=False` and clears the token after N seconds.

**Module responsibilities**:
- `connection.py`: `ConnectionBase` (abstract), `Connection` (sync), `AsyncConnection` (async). URL construction, request building, auth orchestration, error wrapping.
- `platform.py`: `AuthMixin`/`AsyncAuthMixin` for Platform. OAuth client-credentials (`/oauth/token`) or basic auth (`/login`). Dynamic `Platform`/`AsyncPlatform` classes. `platform_factory()`.
- `gateway.py`: `AuthMixin`/`AsyncAuthMixin` for Gateway. Basic auth only (`/login`). Sets `base_path="/api/v2.0"`. `gateway_factory()`.
- `logging.py`: Wraps stdlib `logging`. Adds TRACE (5), FATAL (90), NONE (100) levels. `@trace` decorator logs function entry/exit with timing. Sensitive-data filtering via `heuristics`. Logger cached via `functools.cache`.
- `heuristics.py`: Singleton `Scanner` with compiled regex patterns for API keys, bearer tokens, JWTs, passwords, secrets, etc. Redacts matches in log messages.
- `exceptions.py`: `IpsdkError → RequestError / HTTPStatusError / SerializationError`. Wraps httpx exceptions and exposes `.request`/`.response` properties.
- `http.py`: `HTTPMethod` enum (stdlib 3.11+ or fallback), `Request` and `Response` wrapper classes. `Response` wraps `httpx.Response` with `json()`, `is_success()`, `is_error()`.
- `jsonutils.py`: Thin wrappers around `json.loads`/`json.dumps` that raise `SerializationError` on failure.
- `metadata.py`: Package name, author, version (via `importlib.metadata`).
- `__init__.py`: Public API: exports `platform_factory`, `gateway_factory`, `logging`, `__version__`. Calls `logging.initialize()` on import.

**Key design decision**: `from __future__ import annotations` is used in most source files, placed *after* the copyright header and *before* the module docstring. This is non-standard placement but functional. Not all files include it (`__init__.py` and `jsonutils.py` omit it).

**Base URL behavior**:
- Platform: `https://host:port` (no prefix — callers pass full paths like `/api/v2.0/workflows`)
- Gateway: `https://host:port/api/v2.0` (prefix baked in — callers pass resource paths like `/devices`)

Port auto-resolution: if `port=0` (default), uses 443 for TLS, 80 without. Ports 80 and 443 are not appended to the host string; non-standard ports are.

## Development Commands

```bash
# Setup: requires uv
uv sync --all-extras --dev

# Daily workflow
make test              # pytest
make coverage          # pytest --cov (100% required)
make lint              # ruff check
make format            # ruff format
make typecheck         # mypy static type checking
make security          # bandit security scan
make license           # Check GPL headers
make license-fix       # Add missing headers
make ci                # Run all checks (use before commit)

# Multi-version testing
uv run tox             # All versions sequentially
uv run tox -p auto     # Parallel
uv run tox -e py310    # Specific version
uv run tox -e ci       # Full CI checks via tox

# Tox environments
tox -e coverage        # Coverage report
tox -e lint            # Ruff check only
tox -e format          # Ruff format only
tox -e security        # Bandit scan only
tox -e ci              # All checks
```

**Note**: `make ci` includes the license header check; `tox -e ci` does not. Run `make ci` locally before pushing.

CI (`ci.yaml`): runs lint, format-check, typecheck, security, license, then a matrix test run with `--cov-fail-under=95`.

## Code Standards

**Non-negotiable**:
- GPL-3.0 header on every `.py` file (checked by `make license`)
- 100% test coverage enforced locally; CI enforces 95% threshold
- `str | None` not `Optional[str]`, `dict[str, Any]` not `Dict` (modern union syntax)
- Google-style docstrings with Args/Returns/Raises on all public methods
- No bare `except:`. Catch specific exceptions; bare `except Exception` only when re-raising
- `__slots__` on classes with fixed attributes (`ConnectionBase`, `Request`, `Response`)
- `@logging.trace` on every method/function for TRACE-level debugging
- Early return for validation; raise `IpsdkError` with a descriptive message string

**Patterns**:
- Factory functions create objects; don't instantiate connection classes directly
- Auth mixins contain all auth logic; `ConnectionBase`/`Connection`/`AsyncConnection` are auth-agnostic
- Modifying auth: edit mixins in `platform.py`/`gateway.py`, NOT `connection.py`

## Authentication Credential Rules

- Platform: provide `client_id`+`client_secret` for OAuth, OR `user`+`password` for basic auth. Defaults are `user="admin"`, `password="admin"` — OAuth is only used if `client_id` is explicitly provided.
- Gateway: always basic auth. Defaults are `user="admin@itential"`, `password="admin"`. No OAuth support; `client_id`/`client_secret` are not accepted.
- Never mix OAuth + basic auth params.

## Known Issues

**Missing `.pre-commit-config.yaml`**: `pre-commit` is listed as a dev dependency but the config file doesn't exist in the repo.

## Gotchas

- `want_async=False` by default — easy to forget when you need async
- Platform's `user="admin"` and `password="admin"` defaults mean if you don't pass `client_id`, it silently falls back to basic auth with those defaults
- `gateway_factory` does not accept `client_id`/`client_secret` — Gateway is basic-auth only
- `logging.initialize()` is called on `import ipsdk`, resetting all handlers. Configure logging **after** import.
- `Scanner` in `heuristics.py` is a singleton. Call `Scanner.reset_singleton()` in tests that need a fresh scanner state.
- Port 80 and 443 are not appended to the host URL (httpx compatibility); other ports are appended as `host:port`
- The `HTTPMethod` compatibility shim in `http.py`: Python 3.10 gets the fallback enum, 3.11+ gets the stdlib one. They behave identically but are different types — don't compare them across versions

## Testing

**Organization**: `tests/test_<module>.py` mirrors `src/ipsdk/<module>.py`.

**Strategy**: Unit tests only. All httpx calls are mocked — no network required. `pytest-asyncio` for async tests.

```bash
uv run pytest tests/test_connection.py -v -s -k "test_send_request"
uv run pytest tests/ -v --cov=src/ipsdk --cov-report=term
```

## Build & Release

```bash
# Version comes from git tags
git tag v0.9.0
git push origin v0.9.0
# → GitHub Actions auto-publishes to PyPI (trusted publisher, no token/twine)
```

**CHANGELOG.md must be updated before tagging.** Version is read from installed package metadata at runtime (`importlib.metadata`), not from a hardcoded string.

## Key Files

- `pyproject.toml`: Build config, dependencies, ruff rules, bandit config
- `Makefile`: All dev commands
- `tox.ini`: Multi-version testing, 10 environments: py310–py314, coverage, lint, format, security, ci
- `CHANGELOG.md`: Detailed release history
- `scripts/check_license_headers.py`: License header checker/fixer
- `.github/workflows/ci.yaml`: CI pipeline (lint, security, test matrix)
