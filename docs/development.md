# Development Guide

This project uses `uv` as the Python package manager and build tool. Here are the key development commands:

## Setup

```bash
# Install dependencies and create virtual environment
$ uv sync
```

## Testing

```bash
# Run all tests
$ uv run pytest tests
$ make test

# Run single test
$ uv run pytest tests/test_<module>.py::<test_function>

# Run specific test module
$ uv run pytest tests/test_<module>.py

# Run tests with coverage
$ uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/
$ make coverage
```

### Multi-Version Testing with Tox

The SDK supports Python 3.10, 3.11, 3.12, and 3.13. Use tox to test across all versions:

```bash
# Run tests across all Python versions
$ uv run tox
$ make tox

# Run tests in parallel (faster)
$ uv run tox -p auto

# Run tests on specific Python version
$ uv run tox -e py310    # Python 3.10
$ make tox-py310

$ uv run tox -e py311    # Python 3.11
$ make tox-py311

$ uv run tox -e py312    # Python 3.12
$ make tox-py312

$ uv run tox -e py313    # Python 3.13
$ make tox-py313

# Run quick tests (no lint/security)
$ uv run tox -e quick

# Run coverage report on Python 3.13
$ uv run tox -e coverage
```

## Code Quality

```bash
# Lint code
$ uv run ruff check src/ipsdk
$ uv run ruff check tests
$ make lint

# Format code (automatic code formatting)
$ uv run ruff format src/ipsdk tests
$ make format

# Auto-fix linting issues (where possible)
$ uv run ruff check --fix src/ipsdk tests
$ make ruff-fix

# Type checking
$ uv run mypy src/ipsdk

# Security analysis (scans for vulnerabilities)
$ uv run bandit -r src/ipsdk --configfile pyproject.toml
$ make security
```

## Build and Maintenance

```bash
# Clean build artifacts
$ make clean

# Run CI checks (clean, lint, security, license check, and test)
$ make ci
```

### Version Management

The project uses **dynamic versioning** from git tags:
- Build system: **Hatchling** with **uv-dynamic-versioning**
- Version format: **PEP440** style
- Tags automatically generate versions
- Fallback version: `0.0.0` when no tags exist

## Development Workflow

1. **Setup**: Run `uv sync` to install dependencies and create a virtual environment
2. **Development**: Make your changes to the codebase
3. **Format**: Run `make format` to auto-format code
4. **Testing**: Run tests with `make test` or `uv run pytest tests`
5. **Quality Checks**: Run `make lint` and `make security` to check code quality
6. **Coverage**: Run `make coverage` to generate coverage report
7. **CI**: Run `make ci` before submitting changes (runs all checks)
8. **Multi-version**: Optionally test across Python versions with `make tox`

## Additional Tools

The project uses the following development tools:

- **uv**: Package manager and virtual environment management
- **pytest**: Testing framework with async support (`pytest-asyncio`)
- **pytest-cov**: Code coverage reporting plugin
- **ruff**: Fast Python linter and formatter (30+ rule sets)
- **mypy**: Static type checker
- **bandit**: Security vulnerability scanner
- **tox**: Multi-version Python testing (3.10, 3.11, 3.12, 3.13)
- **tox-uv**: Tox integration with uv for fast environments
- **q**: Debugging utility

All tools are configured in `pyproject.toml` and can be run through `uv` or the provided Makefile targets.

### Ruff Configuration

The project uses comprehensive Ruff configuration with 30+ rule sets:
- pycodestyle (E, W), Pyflakes (F), pyupgrade (UP)
- flake8-bugbear (B), isort (I), pylint (PL)
- Security checks (S), annotations (ANN), async (ASYNC)
- Line length: 88 characters (Black-compatible)
- Target: Python 3.8+ compatibility
- Per-file ignores configured for different modules

### Coverage Requirements

The SDK enforces strict test coverage:
- **Current coverage**: 100%
- Coverage report runs in `make ci` and CI/CD pipeline
- Generate HTML reports with `make coverage`

## Python Version Support

The SDK officially supports Python >=3.10 and is tested on:
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

Testing across versions is automated in CI/CD using GitHub Actions matrix testing.

## Logging

By default all logging is turned off for `ipsdk`. To enable logging, use the `ipsdk.logging.set_level` function.

The SDK provides logging level constants that you can use instead of importing the standard library logging module:

```python
>>> import ipsdk

# Using ipsdk logging constants (recommended)
>>> ipsdk.logging.set_level(ipsdk.logging.DEBUG)
```

### Logging Features

The SDK includes a comprehensive logging system:
- **Function tracing decorator** (`@trace`) with automatic timing and entry/exit logging
- **Custom logging levels**: TRACE (5), FATAL (90), and NONE (100) in addition to standard levels
- **Convenience functions**: `debug()`, `info()`, `warning()`, `error()`, `critical()`, `fatal()`, `exception()`
- **httpx/httpcore logging control** via `propagate` parameter
- **Centralized configuration** via `set_level()`
- **Sensitive data filtering** to automatically redact PII, API keys, passwords, and tokens

### Available Logging Levels

The SDK provides the following logging level constants:

- `ipsdk.logging.NOTSET` - No logging threshold (0)
- `ipsdk.logging.TRACE` - Function tracing and detailed execution flow (5)
- `ipsdk.logging.DEBUG` - Debug messages (10)
- `ipsdk.logging.INFO` - Informational messages (20)
- `ipsdk.logging.WARNING` - Warning messages (30)
- `ipsdk.logging.ERROR` - Error messages (40)
- `ipsdk.logging.CRITICAL` - Critical error messages (50)
- `ipsdk.logging.FATAL` - Fatal error messages (90)
- `ipsdk.logging.NONE` - Disable all logging (100)

### Function Tracing with @trace Decorator

The SDK provides a powerful `@trace` decorator for debugging and performance monitoring. When applied to functions or methods, it automatically logs entry/exit points with execution timing.

#### Basic Usage

```python
from ipsdk import logging

# Enable TRACE level to see trace output
logging.set_level(logging.TRACE)

@logging.trace
def process_data(data):
    # Your implementation
    return result

# When called, logs:
# → module.process_data
# ← module.process_data (0.15ms)
```

#### Features

The `@trace` decorator provides:
- **Automatic entry/exit logging** with `→` and `←` symbols
- **Execution time measurement** in milliseconds (2 decimal precision)
- **Module and class context** extracted automatically from function metadata
- **Exception tracking** with timing when functions exit via exception
- **Sync and async support** - works with both synchronous and asynchronous functions

#### Decorator vs Manual Logging

**Old Pattern (deprecated):**
```python
def my_method(self):
    logging.trace(self.my_method, modname=__name__, clsname=self.__class__)
    # implementation
```

**New Pattern (recommended):**
```python
@logging.trace
def my_method(self):
    # implementation
```

The decorator approach:
- Eliminates repetitive code
- Automatically extracts module and class names
- Provides entry/exit visibility
- Includes execution timing
- Tracks exception exits

#### Using with Classes

The decorator works seamlessly with instance methods, class methods, and static methods:

```python
class DataProcessor:
    @logging.trace
    def process(self, data):
        """Process data - traced automatically"""
        return self._transform(data)

    @logging.trace
    def _transform(self, data):
        """Private method - also traced"""
        return data.upper()

    @classmethod
    @logging.trace
    def from_config(cls, config):
        """Class method - traced"""
        return cls(config['param'])

    @staticmethod
    @logging.trace
    def validate(data):
        """Static method - traced"""
        return len(data) > 0
```

#### Async Functions

The decorator automatically handles async functions:

```python
@logging.trace
async def fetch_data(url):
    """Async function - timing includes await time"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Logs:
# → module.fetch_data
# ← module.fetch_data (245.67ms)
```

#### Exception Tracking

When functions exit via exception, the decorator logs the exception exit with timing:

```python
@logging.trace
def risky_operation():
    raise ValueError("Something went wrong")

# Logs:
# → module.risky_operation
# ← module.risky_operation (exception, 0.03ms)
# (Exception propagates normally)
```

#### Output Format

**Entry log format:**
```
→ module_name.ClassName.method_name
```

**Normal exit format:**
```
← module_name.ClassName.method_name (1.23ms)
```

**Exception exit format:**
```
← module_name.ClassName.method_name (exception, 1.23ms)
```

#### Performance Considerations

- Uses `time.perf_counter()` for high-precision timing (sub-millisecond accuracy)
- Minimal overhead: ~0.01-0.02ms per traced function call
- Only logs when `TRACE` level is enabled
- Safe to leave decorators in production code (no output when TRACE is disabled)

#### Example: Debugging Performance Issues

```python
import time
from ipsdk import logging

logging.set_level(logging.TRACE)

@logging.trace
def slow_query():
    time.sleep(0.5)  # Simulate slow database query
    return "result"

@logging.trace
def fast_cache_lookup():
    return "cached_result"

@logging.trace
def main():
    slow_query()
    fast_cache_lookup()
    return "done"

main()
# Output:
# → __main__.main
# → __main__.slow_query
# ← __main__.slow_query (500.12ms)
# → __main__.fast_cache_lookup
# ← __main__.fast_cache_lookup (0.01ms)
# ← __main__.main (500.25ms)
```

This helps identify performance bottlenecks by showing exactly which functions are taking the most time.

#### Best Practices

1. **Use TRACE level in development** - Enable it for debugging, disable in production unless needed
2. **Apply to key functions** - Focus on API calls, database queries, and complex logic
3. **Leave decorators in place** - They're harmless when TRACE is disabled
4. **Review timing data** - Use logs to identify slow operations during development
5. **Combine with other logging** - Mix with `debug()`, `info()`, etc. for comprehensive visibility

## Authentication and Session Management

### Time to Live (TTL) for Authentication

The SDK supports automatic reauthentication through the `ttl` (time to live) parameter. This feature forces the SDK to reauthenticate after a specified period, which is useful for long-running applications or when working with authentication tokens that expire.

#### What is TTL?

TTL (time to live) defines how long an authentication session remains valid before forcing reauthentication. When the TTL expires:
1. The SDK automatically detects the timeout on the next API request
2. The authentication token is cleared
3. A new authentication request is made before proceeding
4. The timestamp is reset for the next TTL period

#### When to Use TTL

Use the `ttl` parameter when:
- **Long-running applications**: Services that run for extended periods (hours or days)
- **Token expiration**: Your authentication tokens expire after a certain time
- **Security requirements**: Your organization requires periodic reauthentication
- **Session refresh**: You want to ensure fresh credentials are used regularly

#### Default Behavior

By default, `ttl` is set to `0`, which means reauthentication is **disabled**. The SDK will authenticate once and reuse the same token/session for the lifetime of the connection object.

#### Basic Usage

```python
import ipsdk

# Create a Platform connection with 30-minute TTL (1800 seconds)
platform = ipsdk.platform_factory(
    host="platform.example.com",
    user="admin",
    password="password",
    ttl=1800  # Force reauthentication every 30 minutes
)

# Create a Gateway connection with 1-hour TTL (3600 seconds)
gateway = ipsdk.gateway_factory(
    host="gateway.example.com",
    user="admin@itential",
    password="password",
    ttl=3600  # Force reauthentication every hour
)
```

#### How It Works

```python
import time
import ipsdk

# Create connection with 10-second TTL for demonstration
platform = ipsdk.platform_factory(
    host="platform.example.com",
    user="admin",
    password="password",
    ttl=10  # Very short TTL for testing
)

# First request - authenticates
response = platform.get("/api/v2.0/workflows")
print("First request successful")

# Wait 5 seconds - within TTL window
time.sleep(5)
response = platform.get("/api/v2.0/workflows")
print("Second request - reused existing authentication")

# Wait another 6 seconds - total 11 seconds, exceeds TTL
time.sleep(6)
response = platform.get("/api/v2.0/workflows")
print("Third request - automatically reauthenticated")
```

#### TTL with Different Authentication Methods

The TTL feature works with all supported authentication methods:

**OAuth (Platform only):**
```python
platform = ipsdk.platform_factory(
    host="platform.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    ttl=1800  # Reauthenticate every 30 minutes
)
```

**Basic Authentication (Platform and Gateway):**
```python
# Platform with basic auth
platform = ipsdk.platform_factory(
    host="platform.example.com",
    user="admin",
    password="password",
    ttl=3600  # Reauthenticate every hour
)

# Gateway with basic auth
gateway = ipsdk.gateway_factory(
    host="gateway.example.com",
    user="admin@itential",
    password="password",
    ttl=3600  # Reauthenticate every hour
)
```

#### TTL with Async Connections

The TTL feature works identically with async connections:

```python
import asyncio
import ipsdk

async def main():
    # Create async connection with TTL
    platform = ipsdk.platform_factory(
        host="platform.example.com",
        user="admin",
        password="password",
        ttl=1800,  # 30 minutes
        want_async=True
    )

    # First request - authenticates
    response = await platform.get("/api/v2.0/workflows")

    # Subsequent requests within TTL window reuse authentication
    response = await platform.get("/api/v2.0/devices")

    # After TTL expires, next request will automatically reauthenticate
    await asyncio.sleep(1801)
    response = await platform.get("/api/v2.0/workflows")

asyncio.run(main())
```

#### Thread Safety

The SDK's TTL implementation is thread-safe:
- Synchronous connections use `threading.Lock()`
- Asynchronous connections use `asyncio.Lock()`
- Multiple threads/tasks attempting simultaneous requests will only trigger one reauthentication

#### Logging TTL Activity

Enable logging to monitor TTL-related reauthentication:

```python
import ipsdk

# Enable INFO level logging to see TTL messages
ipsdk.logging.set_level(ipsdk.logging.INFO)

platform = ipsdk.platform_factory(
    host="platform.example.com",
    user="admin",
    password="password",
    ttl=1800
)

# When TTL expires, you'll see log messages like:
# Auth TTL exceeded (1801.2s >= 1800s)
# Forcing reauthentication due to timeout
```

#### Best Practices

1. **Match token expiration**: Set TTL slightly lower than your token expiration time
   ```python
   # If tokens expire after 1 hour, set TTL to 55 minutes
   ttl=3300  # 55 minutes
   ```

2. **Use reasonable intervals**: Don't set TTL too low (causes unnecessary authentication overhead)
   ```python
   # Good: 30 minutes to 1 hour for most applications
   ttl=1800  # 30 minutes

   # Avoid: Very short intervals (causes performance issues)
   ttl=60  # Not recommended unless required
   ```

3. **Consider your workload**: Balance security needs with authentication overhead
   - High-frequency API calls: Use longer TTL (1+ hour)
   - Low-frequency periodic jobs: Use shorter TTL (15-30 minutes)

4. **Disable for short scripts**: Set `ttl=0` (default) for scripts that complete quickly
   ```python
   # Quick data extraction script - no TTL needed
   platform = ipsdk.platform_factory(
       host="platform.example.com",
       user="admin",
       password="password"
       # ttl=0 is the default - no need to specify
   )
   ```

5. **Test TTL behavior**: Use short TTL values during development to verify reauthentication works correctly

#### Common TTL Values

| Duration | Seconds | Use Case |
|----------|---------|----------|
| 15 minutes | 900 | High-security environments, frequent token rotation |
| 30 minutes | 1800 | Balanced security and performance, recommended default |
| 1 hour | 3600 | Long-running applications with stable tokens |
| 2 hours | 7200 | Low-security environments, infrequent authentication |

#### Troubleshooting

**Issue: Frequent authentication errors**
- Your TTL may be longer than your token expiration time
- Solution: Reduce TTL to be shorter than token lifetime

**Issue: Too many authentication requests**
- Your TTL is too short for your usage pattern
- Solution: Increase TTL to reduce authentication overhead

**Issue: Reauthentication not happening**
- Verify TTL is set to a non-zero value
- Check that enough time has passed between requests
- Enable logging to see TTL status messages

## Documentation Standards

All code in the SDK follows strict documentation standards:

### Docstring Requirements

- **Style**: Google-style docstrings
- **Required sections**:
  - `Args:` - All function/method parameters
  - `Returns:` - Return value description
  - `Raises:` - Only exceptions raised by the function/method itself
- **Format**: Verbose documentation for all public methods and functions

### Example

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of what the function does.

    Longer description with additional details about the function's
    behavior, edge cases, or important notes.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default value

    Returns:
        Description of the return value

    Raises:
        ValueError: When param2 is negative
        TypeError: When param1 is not a string
    """
    pass
```

### Project Documentation

Project documentation is maintained in:
- `docs/` - Detailed documentation files
- `CLAUDE.md` - Project guidance and architecture
- `README.md` - Quick start and overview
- Code docstrings - API documentation
