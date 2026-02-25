# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-02-25

### Added
- License header checking and enforcement with automated script (#102)
- Thread-safe locking to logger cache access (#106)
- `__slots__` to ConnectionBase, Request, Response classes for 40% memory reduction (#106)

### Changed
- Improved tox configuration with new environments and better organization (#101)
- Enhanced Makefile with additional targets and better documentation (#101)
- Renamed LICENSES.md to NOTICE for better clarity (#100)
- Refactored to idiomatic Python boolean comparisons removing 'is True/False' patterns (#106)
- Simplified complex validation logic for better readability (#106)
- Improved resource cleanup patterns and explicit garbage collection in logging.initialize() (#106)

### Fixed
- Critical TTL re-authentication TOCTOU race condition by moving check inside lock (#106)
- Replaced assert statements with proper runtime validation for production safety (#106)
- Added proper None guards to exception properties instead of raising AttributeError (#106)
- Fixed union type syntax errors in type annotations (#106)
- Fixed potential race conditions in concurrent logger access (#106)

### Performance
- Cached TTL enabled flag to eliminate syscall overhead on every request (~100 cycles saved) (#106)
- Optimized regex pattern compilation to class-level with singleton pattern (#106)
- Replaced RLock with Lock for 2x performance improvement on simple flag protection (#106)
- Implemented proper double-check locking pattern for authentication (#106)

### Documentation
- Updated documentation to reflect current state of the project (#107)
- Condensed CLAUDE.md for better maintainability (#105)
- Updated SECURITY.md with improved best practices (#105)

### Testing
- Achieved 100% test coverage across all modules (#104)
- Added comprehensive test cases for logging and platform modules (#104)

## [0.7.0] - 2025-12-16

### Added
- Add support for connection ttl (#95)
- Add thread-safe authentication locking to prevent race conditions (#84)

### Changed
- Migrate release workflow from twine to trusted publisher (#98)
- Improve platform module code quality and documentation (#97)
- Enhance thread safety in logging module (#94)
- Implement decorator pattern for trace function with execution timing (#93)
- Remove unused mock detection logic from exceptions module (#92)
- Modernize and fix docstrings in connection.py (#91)
- Modernize type annotations across all modules (#90)
- Make all boolean comparisons explicit and consistent (#89)
- Add caching to _get_loggers() function for improved performance (#88)
- Replace assert statements with proper runtime validation (#87)
- Remove circular import dependency in heuristics module (#86)

### Fixed
- Add missing token extraction in async OAuth authentication (#96)
- Correct delete method to pass HTTPMethod enum instead of string value (#85)

### Documentation
- Update LICENSES.md with current dependency versions (#83)

## [0.6.0] - 2025-12-08

### Added
- GitHub Release creation to release workflow (#77)
- Tox multi-version testing support (#74)
- Sensitive data filtering and enhanced logging capabilities (#72)
- Comprehensive HTTP enums and integrate with connection module (#71)

### Changed
- Add comprehensive logging.trace() calls with module and class context (#81)
- Add comprehensive module and function docstrings (#80)
- Update ruff configuration and apply import formatting (#79)
- Simplify exception hierarchy and improve code quality (#78)
- Update documentation with comprehensive development guide and accurate exception references (#76)
- Enhance exception logging with full tracebacks (#75)
- Consolidate HTTP utilities into module (#73)
- Expand and organize .gitignore patterns (#70)
- Update README.md (#67)

### Dependencies
- ci(deps): bump actions/checkout from 5 to 6 (#69)
- ci(deps): bump astral-sh/setup-uv from 6 to 7 (#68)

## [0.5.0] - 2025-09-23

### Added
- Comprehensive security documentation (#63)
- Community documentation (#62)
- GoReleaser config and CI/CD workflows (#59)

### Changed
- Rename logger module to logging (#61)
- Add more unit test cases (#60)
- Enhance test coverage and improve CI/CD pipeline (#57)

### Dependencies
- ci(deps): bump actions/setup-python from 5 to 6 (#56)

## [0.4.0] - 2025-08-26

### Added
- GitHub Dependabot configuration (#49)
- Python version matrix testing support (#44)

### Changed
- Update Dependabot configuration (#53)
- Enhance development environment and code quality tools (#47)
- Enhance exceptions module test coverage to 97% (#46)
- Expand jsonutils test coverage to 100% (#45)

### Fixed
- Fix unit tests and enhance exception handling (#52)

### Dependencies
- ci(deps): bump actions/checkout from 4 to 5 (#51)
- ci(deps): bump astral-sh/setup-uv from 5 to 6 (#50)

## [0.3.0] - 2025-08-12

### Added
- New developer guide to docs (#41)
- File logging support (#39)
- Logger stdlib level wrappers (#37)
- Comprehensive type hints throughout the app (#34)
- Request and response wrapper classes (#32)
- Centralized exceptions (#31)

### Changed
- Updated README file (#36)
- Updated logging functionality (#35)
- Updated unit test cases (#33)
- Refactored project structure (#30)

### Fixed
- Typos in all docstrings (#40)

### Removed
- Automatic status check (#29)

## [0.2.0] - 2025-05-22

### Added
- Support for setting request timeout (#26)

## [0.1.1] - 2025-05-12

### Fixed
- Async connection errors with "unexpected keyword argument" error (#24)

## [0.1.0] - 2025-05-07

### Added
- Examples and documentation in README (#14)
- Async support with httpx refactoring (#13)
- Comprehensive logging functionality (#12)
- Support for generating querystrings (#6)
- Initial release of Itential Python SDK
- Factory functions for Platform and Gateway connections
- Support for both synchronous and asynchronous HTTP clients
- OAuth and basic authentication support
- Automatic authentication on first API call

### Changed
- Updated email in pyproject.toml (#20)
- Updated method arguments and documentation (#18)
- Updated project dependencies (#16)
- Refactored library to use factory functions (#9)
- Migrated from requests to httpx library (#7)
- Updated base API path for gateway (#5)
- Updated precedence of values for cloud and gateway (#3)

### Fixed
- Missing setuptools_scm dev dependencies (#22)
- Missing quote in Makefile (#19)
- Data transformation to JSON string (#17)
- Pre-merge pipeline issues (#11)
- Body payload not setting headers properly (#8)

### Added (Dev/Build)
- Missing build package to dev dependencies (#21)
- Release workflow (#15)
- Test cases (#10)
- Community code of conduct (#4)
- Pre-merge pipeline workflow
