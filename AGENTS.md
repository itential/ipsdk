# CLAUDE.md

## What This Is

HTTP client SDK for Itential Platform and Automation Gateway 4.x. Factory-based sync/async clients with auto-authentication, comprehensive logging, and sensitive data filtering. Production-ready despite beta status.

**Current**: v0.8.0 (2026-02-25) | 3.7k LOC | 100% test coverage | Python 3.10-3.13

## Architecture

Factory pattern creates dynamically-typed clients by composing auth mixins with connection base classes at runtime using `type()`. Authentication is thread-locked and happens on first request. Supports OAuth (Platform) and basic auth (Platform/Gateway).

**Core modules**:
- `connection.py`: Abstract base + sync/async HTTP clients using httpx
- `platform.py`/`gateway.py`: Auth mixins that compose with ConnectionBase
- `logging.py`: Custom TRACE/FATAL levels, sensitive data filtering, caching
- `exceptions.py`: IpsdkError → RequestError/HTTPStatusError/SerializationError
- `heuristics.py`: Singleton PII scanner with extensible patterns
- `http.py`: HTTPMethod enum + Request/Response wrappers

**New in 0.8.0**: License header checking with `make license` and `make license-fix` commands

**Previously in 0.7.0**: Connection TTL (`ttl` param forces re-auth after N seconds)

## Stack

**Build**: uv + hatchling + uv-dynamic-versioning (PEP440 from git tags)
**Runtime**: httpx>=0.28.1 (only dependency)
**Dev**: pytest + pytest-asyncio + ruff + mypy + bandit + tox + tox-uv
**CI**: GitHub Actions, trusted publisher to PyPI, matrix Python 3.10-3.13

## Development Commands

```bash
# Daily workflow
make test              # pytest
make coverage          # pytest --cov (100% required)
make lint              # ruff check
make format            # ruff format
make security          # bandit security scan
make license           # Check GPL headers
make license-fix       # Add missing headers
make premerge          # Run all checks (use before commit)

# Multi-version testing
uv run tox             # All versions sequentially
uv run tox -p auto     # Parallel
uv run tox -e py310    # Specific version
uv run tox -e premerge # Full CI checks via tox

# Tox environments
tox -e coverage        # Coverage report
tox -e lint            # Ruff check only
tox -e format          # Ruff format only
tox -e security        # Bandit scan only
tox -e premerge        # All checks
```

## Code Standards

**Non-negotiable**:
- 100% test coverage (enforced, currently at 100%)
- GPL-3.0 license headers on all .py files (checked by `make license`)
- Type hints everywhere: `str | None` not `Optional[str]`, `dict[str, Any]` not `Dict`
- Thread safety: authentication uses `threading.Lock`, loggers are cached
- Google-style docstrings with Args/Returns/Raises
- No bare `except:`, no `assert` in production code (runtime validation with exceptions)
- Line length 88 (Black-compatible), double quotes, single-line imports

**Patterns to follow**:
- Factory functions for object creation, not direct instantiation
- Mixin classes for auth, base classes for HTTP
- Dynamic class creation via `type()` for Platform/AsyncPlatform variants
- Early returns for validation
- Specific exceptions over generic
- `want_async` parameter switches sync/async (default sync)

**Module organization** (user's global preference):
1. Dunder methods first (`__init__`, `__str__`, etc.)
2. Private methods/functions (`_private` or `__internal`)
3. Public methods/functions

## Current Issues

**Type checking broken (22 mypy errors)**:
- logging.py: Custom TRACE/NONE/FATAL levels not in stdlib logging
- heuristics.py: Callable type hints and lambda inference
- exceptions.py: Optional attribute access needs guards (lines 131, 143)
- http.py: HTTPMethod import/redefinition conflicts
- platform.py: Variable not valid as type for return annotations

**Impact**: Type safety unenforced. Runtime works fine but static analysis fails.

**Fix strategy**: Add type stubs or mypy ignore comments for custom logging levels. Add proper None guards in exceptions.py.

**Missing**: `.pre-commit-config.yaml` (referenced in docs but doesn't exist)

## What Not to Break

**Public API surface** (pyproject.toml defines public exports):
- `platform_factory(host, port=443, use_tls=True, verify=True, timeout=30, ttl=0, want_async=False, **auth)`
- `gateway_factory(host, port=443, use_tls=True, verify=True, timeout=30, ttl=0, want_async=False, user=..., password=...)`
- Auth kwargs: `client_id`+`client_secret` OR `user`+`password` (not mixed)

**Thread safety requirements**:
- Authentication must remain locked (prevents race conditions)
- Logger caching must be thread-safe
- Multiple client instances should not share state

**Authentication flow**:
- First request triggers auth via mixin `authenticate()` method
- OAuth extracts bearer token, basic auth gets session cookies
- TTL support: re-auth after `ttl` seconds if configured

**Base paths**:
- Platform: `https://host:port` (no prefix)
- Gateway: `https://host:port/api/v2.0`

## Development Workflow

**Adding features**:
1. Read module docstrings first (100+ lines each, comprehensive)
2. Write tests before code (TDD enforced by coverage)
3. Run `make premerge` before commit
4. Update docstrings if changing signatures

**Modifying auth**: Edit mixins in platform.py/gateway.py, NOT connection.py
**Modifying HTTP**: Edit ConnectionBase/Connection/AsyncConnection together
**Adding sensitive patterns**: Edit `heuristics.py` default patterns
**Adding exceptions**: Inherit from IpsdkError, update hierarchy

## Testing

**Organization**: tests/test_<module>.py mirrors src/ipsdk/<module>.py
**Strategy**: Unit tests only, mock all httpx responses, no network calls
**Coverage**: 755 lines tested, 0 missed, 100%
**Async**: pytest-asyncio for async tests
**Parallelism**: Python 3.10-3.13 via tox matrix

**Key test files**:
- test_logging.py: 38 test cases covering custom levels, filtering, threading
- test_connection.py: Sync/async paths, auth triggers, error handling
- test_platform.py: OAuth + basic auth flows
- test_exceptions.py: Exception hierarchy and wrapping

## Build & Release

**Versioning**: Git tags → uv-dynamic-versioning → PEP440 version
**Release process**:
1. Update CHANGELOG.md
2. Commit to devel branch
3. Tag: `git tag v0.x.0 && git push origin v0.x.0`
4. GitHub Actions auto-publishes to PyPI (trusted publisher, no twine)
5. GitHub Release created automatically

**Artifacts**: wheel + sdist with LICENSE and NOTICE in dist-info/licenses/

## Common Pitfalls

1. **Default is sync**: Must pass `want_async=True` for async clients
2. **Auth credentials**: Don't mix OAuth + basic auth params
3. **Base paths**: Gateway has `/api/v2.0` prefix, Platform doesn't
4. **Custom logging levels**: TRACE/FATAL won't work with external loggers
5. **Thread safety**: Don't share client instances across threads
6. **TTL parameter**: Set `ttl=N` to force re-auth after N seconds (default 0 = disabled)

## Key Files

- `pyproject.toml`: Build config, dependencies, extensive ruff rules (347 lines)
- `Makefile`: All dev commands, well-documented (139 lines)
- `tox.ini`: Multi-version testing, 8 environments (111 lines)
- `CHANGELOG.md`: Detailed release history
- `.github/workflows/premerge.yaml`: CI pipeline (lint, security, test matrix)

## Contact

Issues: https://github.com/itential/ipsdk/issues
Docs: Module docstrings (comprehensive), README.md examples
