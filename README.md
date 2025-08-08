# ipsdk

The Itential Python SDK provides a client implementation in Python for writing
scripts that can make API calls to Itential Platform or Itential Automation
Gateway 4.x.

## Features

- Easy API requests with automatic authentication
- Support for OAuth and user/password login
- Customizable connection settings
- Centralized logging configuration

## Getting started

## Requirements

- Python 3.8 or higher
- httpx >= 0.28.1

## Installation

Install `ipsdk` using pip:

```bash
$ pip install ipsdk
```

Or using uv (recommended for development):

```bash
$ uv add ipsdk
```

The `ipsdk` package provides factory functions for connecting to either
Itential Platform or Itential Automation Gateway.

The `platform_factory(...)` function creates a connection to Itential Platform
The `gateway_factory(...)` function creates a connection to Itential Automation Gateway

Use one of the factory functions to create a new connection to the server
and send requests.

```python
>>> import ipsdk
>>> platform = ipsdk.platform_factory(host="platform.itential.dev", user="admin@pronghorn")
>>> res = platform.get("/health/server")
>>> res
<Response [200 OK]>
>>> res.text
'{"version":"15.8.10-2023.2.44","release":"2023.2.9"...`
```

The above works the same for Itential Automation Gateway, simply use
`gateway_factory` instead of `platform_factory` to connect to Itential
Automation Gateway.

Itential Python SDK also supports using `asyncio` to connect to servers as
well. The example below demonstrates how to connect to the server using an
async connection.

```python
import asyncio
import ipsdk

async def main():
    p = ipsdk.platform_factory(
        host="platform.itential.dev",
        user="admin@pronghorn",
        want_async=True
    )

    res = await p.get("/adapters")

if __name__ == "__main__":
    asyncio.run(main())
```

The connection object supports the following HTTP methods:

- `GET` - Sends a HTTP GET request to the server and returns the results
- `POST` - Sends a HTTP POST request to the server and returns the results
- `PUT` - Sends a HTTP PUT request to the server and returns the results
- `DELETE` - Sends a HTTP DELETE request to the server and returns the results
- `PATCH` - Sends a HTTP PATCH request to the server and returns the results

The following table shows the keyword arguments for each HTTP method:

 | Keyword  | `GET`         | `POST`   | `PUT`    | `DELETE`      | `PATCH`  |
 |----------|---------------|----------|----------|---------------|----------|
 | `path`   | Required      | Required | Required | Required      | Required |
 | `params` | Optional      | Optional | Optional | Optional      | Optional |
 | `json`   | Not Supported | Optional | Optional | Not Supported | Optional |

The `path` argument specifies the relative path of the URI.   This value is
prepended to the base URL.  The base URL for Itential Platform is `<host>` and
the base URL for Itential Automation Gateway is `<host>/api/v2.0`.

The `params` argument accepts a `dict` object that is transformed into the URL
query string.  For example, if `params={"foo": "bar"}` the resulting query
string would be `?foo=bar`

The `json` argument accepts the payload to send in the request as JSON. This
argument accepts either a `list` or `dict` object. When specified, the data
will automatically be converted to a JSON string and the `Content-Type` and
`Accept` headers will be set to `application/json`.

## Configuration

Both the `platform_factory` and `gateway_factory` functions support
configuration using keyword arguments. The table below shows the keyword
arguments for each function along with their default value.

 | Keyword         | `platform_factory` | `gateway_factory` |
 |-----------------|--------------------|-------------------|
 | `host`          | `localhost`        | `localhost`       |
 | `port`          | `0`                | `0`               |
 | `use_tls`       | `True`             | `True`            |
 | `verify`        | `True`             | `True`            |
 | `user`          | `admin`            | `admin@itential`  |
 | `password`      | `admin`            | `admin`           |
 | `client_id`     | `None`             | Not Supported     |
 | `client_secret` | `None`             | Not Supported     |
 | `timeout`       | `30`               | `30`              |
 | `want_async`    | `False`            | `False`           |

## Development

This project uses `uv` as the Python package manager and build tool. Here are the key development commands:

```bash
# Install dependencies and create virtual environment
$ uv sync

# Run tests
$ uv run pytest tests
$ make test

# Run tests with coverage
$ uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/
$ make coverage

# Lint code
$ uv run ruff check src/ipsdk
$ uv run ruff check tests
$ make lint

# Type checking
$ uv run mypy src/ipsdk

# Clean build artifacts
$ make clean

# Run premerge checks (clean, lint, and test)
$ make premerge
```

## Logging

By default all logging is turned off for `ipsdk`. To enable logging to
`stdout`, use the `ipsdk.logger.set_level` function.

The SDK provides logging level constants that you can use instead of importing the standard library logging module:

```python
>>> import ipsdk

# Using ipsdk logging constants (recommended)
>>> ipsdk.logger.set_level(ipsdk.logger.DEBUG)
```

### Available Logging Levels

The SDK provides the following logging level constants:

- `ipsdk.logger.NOTSET` - No logging threshold (0)
- `ipsdk.logger.DEBUG` - Debug messages (10)
- `ipsdk.logger.INFO` - Informational messages (20)
- `ipsdk.logger.WARNING` - Warning messages (30)
- `ipsdk.logger.ERROR` - Error messages (40)
- `ipsdk.logger.CRITICAL` - Critical error messages (50)
- `ipsdk.logger.FATAL` - Fatal error messages (90)

### File Logging

The SDK supports optional file logging in addition to console logging. You can configure file logging using several approaches:

#### Quick Setup with `configure_file_logging`

The easiest way to enable both console and file logging:

```python
>>> import ipsdk

# Enable both console and file logging
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", level=ipsdk.logger.DEBUG)

# With propagation to httpx/httpcore loggers
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", level=ipsdk.logger.INFO, propagate=True)
```

#### Manual File Handler Management

For more control, you can add and remove file handlers manually:

```python
>>> import ipsdk

# First set the console logging level
>>> ipsdk.logger.set_level(ipsdk.logger.INFO)

# Add a file handler
>>> ipsdk.logger.add_file_handler("/path/to/app.log")

# Add multiple file handlers with different levels
>>> ipsdk.logger.add_file_handler("/path/to/debug.log", level=ipsdk.logger.DEBUG)
>>> ipsdk.logger.add_file_handler("/path/to/errors.log", level=ipsdk.logger.ERROR)

# Remove all file handlers when done
>>> ipsdk.logger.remove_file_handlers()
```

#### Custom Log Formatting

You can specify custom format strings for file handlers:

```python
>>> custom_format = "%(asctime)s [%(levelname)s] %(message)s"
>>> ipsdk.logger.add_file_handler("/path/to/app.log", format_string=custom_format)

# Or with configure_file_logging
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", format_string=custom_format)
```

**Note:** File logging automatically creates parent directories if they don't exist.

## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
