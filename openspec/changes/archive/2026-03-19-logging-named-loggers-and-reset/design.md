## Context

`ipsdk.logging` wraps Python's stdlib `logging` module to provide custom levels (TRACE, FATAL, NONE), PII redaction, and a `@trace` decorator. The entire logging hierarchy is pinned to the `ipsdk` root logger; `_get_loggers()` discovers loggers only under the `("ipsdk", "httpx")` prefix tuple and caches the result.

Downstream libraries that embed ipsdk currently have two bad options: (1) bypass `ipsdk.logging` entirely and use stdlib `logging` directly, losing PII filtering and level integration; or (2) manually manipulate stdlib logger internals. Neither is acceptable for a library that advertises itself as production-ready.

The change is entirely within `src/ipsdk/logging.py` and `tests/test_logging.py`. No new runtime dependencies. No public API removals.

## Goals / Non-Goals

**Goals:**
- `get_logger(name)` returns a named child logger under the `ipsdk` namespace, or the root `ipsdk` logger when `name` is `None` (existing behaviour preserved).
- `reset_logger(name)` strips handlers and restores `propagate=True` on any arbitrary stdlib logger by name, enabling callers to silence or re-route third-party noise without touching stdlib internals.
- A module-level `_extra_logger_prefixes: set[str]` registry lets callers register additional prefixes (e.g., `"httpcore"`) so that `_get_loggers()`, `set_level()`, and `initialize()` automatically manage those loggers alongside `ipsdk.*` and `httpx`.
- `set_level()` and `initialize()` accept an optional `loggers: list[str] | None` parameter that temporarily adds prefixes for a single call (without persisting them to the registry).
- 100 % test coverage on all new paths.

**Non-Goals:**
- Structured/JSON log formatting.
- Per-logger PII filtering rules (filtering is global).
- Hierarchical log level inheritance beyond what stdlib already provides.
- Any changes to `heuristics.py`, `connection.py`, or other modules.

## Decisions

### 1. `get_logger(name)` returns a child under `ipsdk.*`

**Decision**: `get_logger("mylib")` returns `logging.getLogger("ipsdk.mylib")`, not `logging.getLogger("mylib")`.

**Why**: Keeps the entire managed hierarchy under one root. A caller can do `ipsdk.logging.set_level(DEBUG)` and have it apply to all child loggers automatically via stdlib propagation, without needing to enumerate them.

**Alternative considered**: Allow arbitrary logger names (callers pass `"mylib.foo"` and get exactly that logger). Rejected because it breaks the single-root invariant and makes `_get_loggers()` non-deterministic.

### 2. `_extra_logger_prefixes` as a module-level `set`

**Decision**: A module-level `_extra_logger_prefixes: set[str]` stores additional prefixes. A public `register_logger_prefix(prefix: str)` function adds to it. `_get_loggers()` merges `{metadata.name, "httpx"}` with this set at call time.

**Why**: Simple, low-overhead, and thread-safe enough for startup-time registration (no hot-path writes). Avoids a full registry class for what is essentially a small config set.

**Alternative considered**: Accept `extra_prefixes` on `set_level()` / `initialize()` only (no persistent registry). Rejected because callers would have to pass the same list on every call.

### 3. `reset_logger(name)` operates on exact logger name, not prefix

**Decision**: `reset_logger("httpcore")` affects only the logger named `"httpcore"`, not `"httpcore.asyncio"` etc.

**Why**: Surgical control is safer. If a caller wants to reset a whole sub-tree, they call `reset_logger` for each. Prefix-matching would silently affect loggers the caller didn't intend.

**Alternative considered**: Accept a prefix and reset all matching loggers. Rejected — too broad, hard to reason about in library code.

### 4. `@cache` on `_get_loggers()` is retained but always cleared before use

**Decision**: Keep `@cache` on `_get_loggers()` for performance; all public functions that depend on it call `_get_loggers.cache_clear()` before calling `_get_loggers()`. This is already the pattern in `set_level()` and `initialize()`.

**Why**: Loggers are created lazily; without clearing the cache, newly registered child loggers would be missed. Clearing before use is cheap (O(1)) and safe.

## Risks / Trade-offs

- **`get_logger("ipsdk")` and `get_logger(None)` return the same object** — callers who pass the literal string `"ipsdk"` get a child named `"ipsdk.ipsdk"`. Document clearly that `name` should not include the `ipsdk.` prefix. This is a footgun but acceptable given the API is additive and opt-in.
  → Mitigation: docstring example + `ValueError` if `name` starts with `metadata.name + "."`.

- **`reset_logger` on an unknown name is a no-op** — stdlib `logging.getLogger("unknown")` creates a placeholder logger. Resetting it is harmless but may confuse callers who misspell a name.
  → Mitigation: function returns `bool` indicating whether the logger had any handlers or non-default state before the reset.

- **`_extra_logger_prefixes` is not thread-safe for concurrent writes** — registration is expected at import/startup time, not during live request handling.
  → Mitigation: document the startup-only contract; add a `threading.Lock` around writes to be safe.

## Migration Plan

All changes are backwards compatible:
1. `get_logger()` with no arguments: unchanged behaviour.
2. `set_level(lvl)` with no `loggers` argument: unchanged behaviour.
3. `initialize()` with no arguments: unchanged behaviour.

No migration steps required. Ship as a minor version bump (0.8.x → 0.9.0 since it adds public API surface).

## Open Questions

- Should `register_logger_prefix` be idempotent (silently ignore duplicates) or raise on duplicate? Lean toward idempotent.
- Should the `loggers` parameter on `set_level()` / `initialize()` persist to `_extra_logger_prefixes`, or be one-shot? Current decision: one-shot (non-persisting). Revisit if callers find it inconvenient.
