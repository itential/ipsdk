## ADDED Requirements

### Requirement: register_logger_prefix adds a prefix to the managed logger registry
`ipsdk.logging.register_logger_prefix(prefix)` SHALL add the given string to the module-level `_extra_logger_prefixes` set so that subsequent calls to `_get_loggers()`, `set_level()`, and `initialize()` include loggers whose names start with that prefix.

#### Scenario: Registered prefix is included in logger discovery
- **WHEN** `register_logger_prefix("httpcore")` is called
- **AND** `_get_loggers()` is called (with cache cleared)
- **THEN** any existing logger named `"httpcore"` or `"httpcore.*"` is included in the returned set

#### Scenario: Duplicate registration is idempotent
- **WHEN** `register_logger_prefix("httpcore")` is called twice
- **THEN** `_extra_logger_prefixes` contains `"httpcore"` exactly once

### Requirement: _get_loggers includes extra prefixes from the registry
`_get_loggers()` SHALL discover loggers matching `metadata.name`, `"httpx"`, AND every prefix in `_extra_logger_prefixes`.

#### Scenario: Default discovery without extra prefixes
- **WHEN** `_extra_logger_prefixes` is empty
- **THEN** `_get_loggers()` returns only loggers whose names start with `"ipsdk"` or `"httpx"`

#### Scenario: Discovery with extra prefix registered
- **WHEN** `register_logger_prefix("mylib")` has been called
- **AND** `logging.getLogger("mylib.core")` exists in the logging manager
- **THEN** `_get_loggers()` includes the `"mylib.core"` logger

### Requirement: set_level accepts an optional loggers parameter for one-shot management
`set_level(lvl, *, propagate=False, loggers=None)` SHALL accept an optional `loggers: list[str] | None` parameter. When provided, the named loggers SHALL have their level set to `lvl` in addition to the normal managed set. The extra names SHALL NOT be persisted to `_extra_logger_prefixes`.

#### Scenario: One-shot logger level set
- **WHEN** `set_level(DEBUG, loggers=["boto3"])` is called
- **THEN** `logging.getLogger("boto3").level` is `DEBUG`
- **AND** `"boto3"` is NOT in `_extra_logger_prefixes` after the call

### Requirement: initialize accepts an optional loggers parameter for one-shot initialization
`initialize(loggers=None)` SHALL accept an optional `loggers: list[str] | None` parameter. When provided, the named loggers SHALL be reset (handlers cleared, level set to NONE) in addition to the normally managed set. The extra names SHALL NOT be persisted to `_extra_logger_prefixes`.

#### Scenario: One-shot logger initialization
- **WHEN** `initialize(loggers=["urllib3"])` is called
- **THEN** `logging.getLogger("urllib3")` has a single `StreamHandler` pointing to `stderr`
- **AND** its level is `NONE`
- **AND** `"urllib3"` is NOT in `_extra_logger_prefixes` after the call

### Requirement: registry writes are thread-safe
`register_logger_prefix` SHALL use the existing `_logger_cache_lock` (or an equivalent lock) to protect writes to `_extra_logger_prefixes`.

#### Scenario: Concurrent registration
- **WHEN** multiple threads call `register_logger_prefix` concurrently with different prefixes
- **THEN** all prefixes are present in `_extra_logger_prefixes` after all threads complete
- **AND** no `RuntimeError` or data corruption occurs
