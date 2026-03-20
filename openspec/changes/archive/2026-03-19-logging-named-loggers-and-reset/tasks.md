## 1. Registry Infrastructure

- [x] 1.1 Add `_extra_logger_prefixes: set[str]` module-level set and `_registry_lock = threading.Lock()` to `logging.py`
- [x] 1.2 Implement `register_logger_prefix(prefix: str) -> None` with lock-protected write and idempotent set insertion
- [x] 1.3 Update `_get_loggers()` to merge `{metadata.name, "httpx"}` with `_extra_logger_prefixes` when discovering loggers

## 2. Named Loggers

- [x] 2.1 Update `get_logger(name: str | None = None)` signature and add `ValueError` guard when `name` starts with `metadata.name + "."`
- [x] 2.2 Return `logging.getLogger(f"{metadata.name}.{name}")` for non-None names; preserve existing root-logger path for `None`

## 3. Dependency Logger Reset

- [x] 3.1 Implement `reset_logger(name: str) -> bool` — capture pre-reset state (handlers + level), call `handler.close()` on each, remove handlers, set level to `NOTSET`, set `propagate=True`, return bool
- [x] 3.2 Export `reset_logger` in module public surface (add to module-level docstring listing)

## 4. One-shot loggers Parameter

- [x] 4.1 Add `loggers: list[str] | None = None` keyword-only parameter to `set_level()`; when provided, set level on each named logger in addition to the managed set (do not persist to registry)
- [x] 4.2 Add `loggers: list[str] | None = None` keyword-only parameter to `initialize()`; when provided, apply the same handler-clear + stderr-handler + NONE-level treatment to each named logger (do not persist to registry)

## 5. Tests

- [x] 5.1 Add tests for `get_logger(None)` and `get_logger()` return the `ipsdk` root logger (regression)
- [x] 5.2 Add tests for `get_logger("mylib")` returns logger named `"ipsdk.mylib"` and same instance on second call
- [x] 5.3 Add test for `get_logger("ipsdk.mylib")` raises `ValueError`
- [x] 5.4 Add tests for `reset_logger` on a logger with handlers: handlers removed, closed, level reset, propagate True, returns True
- [x] 5.5 Add test for `reset_logger` on a logger with no handlers and NOTSET level returns False
- [x] 5.6 Add tests for `register_logger_prefix` — idempotent, appears in `_extra_logger_prefixes`, discovered by `_get_loggers()`
- [x] 5.7 Add tests for `set_level(lvl, loggers=["somelib"])` sets level on the named logger without persisting to registry
- [x] 5.8 Add tests for `initialize(loggers=["somelib"])` clears and reinitializes the named logger without persisting to registry
- [x] 5.9 Verify 100% coverage (`make coverage`) passes with no new uncovered lines

## 6. Docs & Cleanup

- [x] 6.1 Update module docstring in `logging.py` to document new public functions (`get_logger` signature, `reset_logger`, `register_logger_prefix`)
- [x] 6.2 Run `make ci` and confirm all checks pass
