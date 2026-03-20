## ADDED Requirements

### Requirement: Response exposes started_at timestamp
Every `Response` object SHALL expose a `started_at` attribute containing the UTC wall-clock time immediately before `client.send()` was called, formatted as an ISO 8601 string (e.g., `"2024-01-15T10:30:00.123456+00:00"`).

#### Scenario: started_at is present on successful response
- **WHEN** any HTTP method (GET, POST, PUT, PATCH, DELETE) completes successfully
- **THEN** `response.started_at` is a non-empty ISO 8601 UTC string

#### Scenario: started_at is present on error response
- **WHEN** the server returns a 4xx or 5xx status and `HTTPStatusError` is raised
- **THEN** the exception's wrapped response does not expose `started_at` (timing is on `Response`, which is only constructed on success)

### Requirement: Response exposes finished_at timestamp
Every `Response` object SHALL expose a `finished_at` attribute containing the UTC wall-clock time immediately after `client.send()` returned, formatted as an ISO 8601 string.

#### Scenario: finished_at is present on successful response
- **WHEN** any HTTP method completes successfully
- **THEN** `response.finished_at` is a non-empty ISO 8601 UTC string

#### Scenario: finished_at is after started_at
- **WHEN** any HTTP method completes successfully
- **THEN** `response.finished_at` >= `response.started_at` (lexicographic ISO 8601 comparison is valid for UTC)

### Requirement: Response exposes elapsed_ms
Every `Response` object SHALL expose an `elapsed_ms` attribute containing the integer number of milliseconds elapsed between `started_at` and `finished_at`.

#### Scenario: elapsed_ms is non-negative integer
- **WHEN** any HTTP method completes successfully
- **THEN** `response.elapsed_ms` is an `int` >= 0

#### Scenario: elapsed_ms is consistent with timestamps
- **WHEN** `started_at` and `finished_at` are parsed as datetime objects
- **THEN** `elapsed_ms` equals `int((finished_at - started_at).total_seconds() * 1000)`

### Requirement: All HTTP methods include timing on returned Response
The sync methods `get`, `post`, `put`, `patch`, `delete` on `Connection` and the async equivalents on `AsyncConnection` SHALL all return a `Response` with valid `started_at`, `finished_at`, and `elapsed_ms` values.

#### Scenario: Sync GET includes timing
- **WHEN** `connection.get(path)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Sync POST includes timing
- **WHEN** `connection.post(path, json=payload)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Sync PUT includes timing
- **WHEN** `connection.put(path, json=payload)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Sync PATCH includes timing
- **WHEN** `connection.patch(path, json=payload)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Sync DELETE includes timing
- **WHEN** `connection.delete(path)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Async GET includes timing
- **WHEN** `await async_connection.get(path)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated

#### Scenario: Async POST includes timing
- **WHEN** `await async_connection.post(path, json=payload)` returns a response
- **THEN** `response.started_at`, `response.finished_at`, and `response.elapsed_ms` are all populated
