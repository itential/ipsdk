## 1. Update Response class

- [x] 1.1 Add `_started_at` and `_finished_at` to `Response.__slots__` in `src/ipsdk/http.py`
- [x] 1.2 Update `Response.__init__` to accept `started_at: str` and `finished_at: str` keyword arguments and assign to slots
- [x] 1.3 Add `started_at` property returning `self._started_at`
- [x] 1.4 Add `finished_at` property returning `self._finished_at`
- [x] 1.5 Add `elapsed_ms` property computing `int((datetime.fromisoformat(self._finished_at) - datetime.fromisoformat(self._started_at)).total_seconds() * 1000)`
- [x] 1.6 Update `Response.__repr__` if desired (optional — keep it minimal)

## 2. Update sync _send_request

- [x] 2.1 Import `datetime` and `timezone` from stdlib in `src/ipsdk/connection.py`
- [x] 2.2 Capture `started_at = datetime.now(timezone.utc)` immediately before `self.client.send(request)` in `Connection._send_request`
- [x] 2.3 Capture `finished_at = datetime.now(timezone.utc)` immediately after `self.client.send(request)` returns
- [x] 2.4 Pass `started_at=started_at.isoformat()` and `finished_at=finished_at.isoformat()` to `Response(res, ...)`

## 3. Update async _send_request

- [x] 3.1 Capture `started_at = datetime.now(timezone.utc)` immediately before `await self.client.send(request)` in `AsyncConnection._send_request`
- [x] 3.2 Capture `finished_at = datetime.now(timezone.utc)` immediately after `await self.client.send(request)` returns
- [x] 3.3 Pass `started_at=started_at.isoformat()` and `finished_at=finished_at.isoformat()` to `Response(res, ...)`

## 4. Update tests

- [x] 4.1 Update all existing `Response(mock_httpx_response)` constructions in `tests/test_http.py` to include `started_at` and `finished_at` keyword args
- [x] 4.2 Add tests for `Response.started_at`, `Response.finished_at`, and `Response.elapsed_ms` properties
- [x] 4.3 Verify `elapsed_ms` is consistent with the two timestamps in a test
- [x] 4.4 Update `tests/test_connection.py` to assert `started_at`, `finished_at`, and `elapsed_ms` are present on responses from all HTTP methods (GET, POST, PUT, PATCH, DELETE — both sync and async)

## 5. Verify

- [x] 5.1 Run `make ci` and confirm all checks pass with 100% coverage
