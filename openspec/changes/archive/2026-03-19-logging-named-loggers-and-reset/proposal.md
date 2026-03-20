## Why

The `ipsdk` logging module currently hardcodes its logger hierarchy under the `ipsdk` namespace and `_get_loggers()` only discovers `ipsdk.*` and `httpx` loggers — making it impossible for downstream libraries or application code to create named child loggers, or to suppress/reset noise from arbitrary third-party dependencies (e.g., `httpcore`, `urllib3`, `boto3`) without reaching into stdlib `logging` directly. Libraries that embed ipsdk need a first-class API to integrate their own named loggers into ipsdk's level/filter/handler management.

## What Changes

- Add `get_logger(name: str | None = None)` — when `name` is provided, returns a named child logger under the `ipsdk` namespace (e.g., `ipsdk.mylib`); when `None`, returns the root `ipsdk` logger (existing behaviour).
- Add `reset_logger(name: str)` — removes all handlers, resets level, and sets `propagate=True` on any arbitrary logger by name (e.g., `"httpcore"`, `"boto3"`), letting it fall through to Python's root handler or be silenced.
- Extend `set_level()` / `initialize()` to accept an optional `loggers: list[str] | None` parameter so callers can bring additional named loggers under ipsdk management without touching `propagate` internals directly.
- Update `_get_loggers()` to honour a configurable registry of extra logger names/prefixes, not just the hardcoded `("ipsdk", "httpx")` tuple.

## Capabilities

### New Capabilities

- `named-loggers`: Create and retrieve named child loggers under the `ipsdk` hierarchy via `get_logger(name)`.
- `dependency-logger-reset`: Reset (clear handlers, restore propagation) arbitrary third-party loggers by name via `reset_logger(name)`.
- `managed-logger-registry`: A configurable registry of extra logger prefixes that `_get_loggers()`, `set_level()`, and `initialize()` operate on, replacing the hardcoded `("ipsdk", "httpx")` tuple.

### Modified Capabilities

<!-- No existing spec-level capabilities are changing requirements. -->

## Impact

- `src/ipsdk/logging.py`: All changes are contained here.
- `get_logger()` signature changes (adds optional `name` parameter) — backwards compatible; existing callers with no argument continue to work.
- `set_level()` and `initialize()` gain optional `loggers` parameter — backwards compatible.
- `_get_loggers()` internal logic changes; its `@cache` is still cleared on each `set_level`/`initialize` call.
- Tests: `tests/test_logging.py` will need new coverage for all three new capabilities.
- No new runtime dependencies.
