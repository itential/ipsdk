## ADDED Requirements

### Requirement: get_logger returns root logger when name is None
`ipsdk.logging.get_logger()` and `ipsdk.logging.get_logger(None)` SHALL both return the `logging.Logger` instance registered under the `ipsdk` root name, preserving existing behaviour.

#### Scenario: Call with no argument
- **WHEN** `get_logger()` is called with no arguments
- **THEN** the returned logger's name is `"ipsdk"`

#### Scenario: Call with None
- **WHEN** `get_logger(None)` is called
- **THEN** the returned logger's name is `"ipsdk"`

### Requirement: get_logger returns named child logger under ipsdk namespace
When a non-None `name` is passed, `get_logger(name)` SHALL return a `logging.Logger` whose full name is `"ipsdk.<name>"`.

#### Scenario: Named child logger
- **WHEN** `get_logger("mylib")` is called
- **THEN** the returned logger's name is `"ipsdk.mylib"`

#### Scenario: Same instance on repeated calls
- **WHEN** `get_logger("mylib")` is called twice
- **THEN** both calls return the identical `Logger` object (stdlib behaviour via `logging.getLogger`)

### Requirement: get_logger rejects names that already include the ipsdk prefix
If `name` starts with `"ipsdk."`, `get_logger` SHALL raise `ValueError` to prevent double-prefixing (e.g., `"ipsdk.ipsdk.mylib"`).

#### Scenario: Prefix already present
- **WHEN** `get_logger("ipsdk.mylib")` is called
- **THEN** `ValueError` is raised with a message indicating the prefix must not be included

### Requirement: Named child loggers propagate to the ipsdk root by default
Child loggers returned by `get_logger(name)` SHALL have `propagate=True` (stdlib default) so that level changes on the `ipsdk` root logger apply automatically.

#### Scenario: Level inheritance via propagation
- **WHEN** `set_level(DEBUG)` is called on the module
- **AND** `get_logger("mylib")` is called after
- **THEN** the child logger propagates records up to the `ipsdk` root handler
