## Why

Callers have no visibility into how long HTTP requests take — there's no way to measure latency, detect slow endpoints, or correlate response times with application behavior without wrapping every call externally. Adding `started_at`, `finished_at`, and `elapsed_ms` directly to `Response` makes timing a first-class part of the SDK's contract.

## What Changes

- `Response` gains three new read-only attributes: `started_at` (ISO 8601 UTC string), `finished_at` (ISO 8601 UTC string), and `elapsed_ms` (int milliseconds)
- `_send_request` in both `Connection` and `AsyncConnection` captures wall-clock timestamps around `client.send()` and passes them to `Response`
- `Response.__init__` signature expands to accept `started_at` and `finished_at`; `elapsed_ms` is derived

## Capabilities

### New Capabilities
- `response-timing`: Timing metadata (`started_at`, `finished_at`, `elapsed_ms`) on every `Response` object returned from any HTTP method

### Modified Capabilities

## Impact

- `src/ipsdk/http.py`: `Response` class — new `__slots__`, new constructor params, three new properties
- `src/ipsdk/connection.py`: `Connection._send_request` and `AsyncConnection._send_request` — timing capture around `client.send()`
- `tests/test_http.py`: new assertions on `Response` timing attributes
- `tests/test_connection.py`: verify timing is populated on responses from all HTTP methods
