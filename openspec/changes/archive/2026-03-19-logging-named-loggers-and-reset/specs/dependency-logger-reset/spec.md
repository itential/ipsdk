## ADDED Requirements

### Requirement: reset_logger clears handlers and restores propagation on any named logger
`ipsdk.logging.reset_logger(name)` SHALL remove all handlers from the named stdlib logger, reset its level to `NOTSET`, and set `propagate=True`, regardless of whether the logger is in the ipsdk namespace.

#### Scenario: Reset a third-party logger
- **WHEN** `reset_logger("httpcore")` is called
- **THEN** `logging.getLogger("httpcore")` has no handlers
- **AND** its level is `logging.NOTSET`
- **AND** its `propagate` attribute is `True`

#### Scenario: Reset an ipsdk child logger
- **WHEN** a child logger `"ipsdk.mylib"` has been configured with handlers and a level
- **AND** `reset_logger("ipsdk.mylib")` is called
- **THEN** `logging.getLogger("ipsdk.mylib")` has no handlers and level `NOTSET`

### Requirement: reset_logger returns True if the logger had non-default state
`reset_logger` SHALL return `True` if the logger had at least one handler OR a non-NOTSET level before the reset, and `False` otherwise.

#### Scenario: Logger had handlers
- **WHEN** `logging.getLogger("httpcore")` has one or more handlers attached
- **AND** `reset_logger("httpcore")` is called
- **THEN** the return value is `True`

#### Scenario: Logger had no handlers or level
- **WHEN** `logging.getLogger("unknown.lib")` has no handlers and level `NOTSET`
- **AND** `reset_logger("unknown.lib")` is called
- **THEN** the return value is `False`

### Requirement: reset_logger closes handlers before removing them
`reset_logger` SHALL call `handler.close()` on each handler before removing it, consistent with how `initialize()` manages handlers.

#### Scenario: Handler is closed
- **WHEN** a logger has a `StreamHandler` attached
- **AND** `reset_logger` is called
- **THEN** the handler's `close()` method is called exactly once before it is removed
