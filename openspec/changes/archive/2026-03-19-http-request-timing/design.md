## Context

`Response` in `http.py` currently wraps `httpx.Response` with a single `_response` slot. Timing is not captured anywhere in the SDK. The `_send_request` method in both `Connection` and `AsyncConnection` is the single choke point through which all HTTP methods pass — it is the correct and only place to capture wall-clock timing.

`httpx.Response` exposes an `elapsed` property (`datetime.timedelta`) that measures time from sending the request to receiving the full response body. However, this only covers the network I/O window; it does not include the time spent building the request or any SDK-side pre/post processing. Using httpx's `elapsed` would also couple `Response` to httpx's internal timing model, which is inconsistent with the SDK's goal of owning its abstraction layer.

## Goals / Non-Goals

**Goals:**
- `Response` exposes `started_at` (UTC ISO 8601 string), `finished_at` (UTC ISO 8601 string), and `elapsed_ms` (int)
- Timing covers the wall-clock window around `client.send()` in `_send_request`
- Both sync and async paths capture identical fields
- `elapsed_ms` is always an integer (truncated, not rounded)

**Non-Goals:**
- Sub-millisecond precision — milliseconds are sufficient for API latency use cases
- Timing of auth flows (`authenticate()`) — only the actual HTTP send is timed
- Streaming responses — out of scope (SDK doesn't support streaming today)
- Exposing raw `datetime` objects on `Response` — strings keep the public API simple and JSON-serializable

## Decisions

**Decision: Capture timing in `_send_request`, not in HTTP method wrappers**

All five HTTP methods (`get`, `post`, `put`, `patch`, `delete`) delegate to `_send_request`. Capturing timing there means one change covers all methods in both sync and async clients, with zero risk of forgetting a method. Alternative (capturing in each method wrapper) would require 10 changes and create a maintenance surface.

**Decision: Store `started_at`/`finished_at` as ISO 8601 UTC strings, derive `elapsed_ms` as a property**

Strings are immediately useful (logging, JSON serialization) without requiring callers to format. `elapsed_ms` as a computed property avoids storing redundant state — it is always `(finished_at_dt - started_at_dt).total_seconds() * 1000`. Alternative (storing `datetime` objects) would expose a httpx-adjacent type on the public API and require callers to format for logging.

**Decision: Use `datetime.now(timezone.utc)` not `time.time()`**

`time.time()` would require manual ISO formatting. `datetime.now(timezone.utc)` gives a tz-aware object that `.isoformat()` formats correctly. The `elapsed_ms` calculation (`(finished - started).total_seconds() * 1000`) is cleaner with `timedelta` arithmetic than float subtraction.

**Decision: `elapsed_ms` is `int`, not `float`**

Sub-millisecond precision is not meaningful for API latency. Truncating to `int` with `int(...)` (not `round`) keeps the semantics simple: `elapsed_ms` is always a whole number of milliseconds.

**Decision: Expand `Response.__slots__` with `_started_at` and `_finished_at`**

The class already uses `__slots__` for memory efficiency. Two additional slots are cheap. `elapsed_ms` is a derived property and does not need a slot.

## Risks / Trade-offs

- **Breaking change to `Response.__init__` signature** → Mitigation: `started_at` and `finished_at` are keyword-only with no defaults, which is intentional — the only callsite is `_send_request`, so there are no external callers to break (the class is not part of the public API surface beyond its properties).
- **Test mocks need updating** → Any test that constructs `Response(mock_httpx_response)` directly will need to pass timing values. This is a small, mechanical change.

## Migration Plan

1. Update `Response.__init__` and `__slots__` in `http.py`
2. Update both `_send_request` implementations in `connection.py`
3. Update `tests/test_http.py` and `tests/test_connection.py`
4. Run `make ci` to verify 100% coverage and all checks pass
