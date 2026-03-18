# ipsdk

[![PyPI version](https://badge.fury.io/py/ipsdk.svg)](https://badge.fury.io/py/ipsdk)
[![Python Versions](https://img.shields.io/pypi/pyversions/ipsdk.svg)](https://pypi.org/project/ipsdk/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Tests](https://github.com/itential/ipsdk/workflows/Run%20CI%20pipeline/badge.svg)](https://github.com/itential/ipsdk/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-green)](https://github.com/itential/ipsdk)

> Python SDK for making API calls to Itential Platform and Itential Automation Gateway 4.x.

Provides sync and async HTTP clients with automatic authentication, session management, and sensitive data filtering. Single runtime dependency: [httpx](https://www.python-httpx.org/).

## Installation

```bash
pip install ipsdk
```

Or with uv:

```bash
uv add ipsdk
```

Requires Python 3.10+.

## Python Version Support

| Version | Status  |
|---------|---------|
| 3.10    | Supported |
| 3.11    | Supported |
| 3.12    | Supported |
| 3.13    | Supported |
| 3.14    | Supported |
| 3.15    | Beta    |

## Usage

### Platform — basic auth

```python
import ipsdk

platform = ipsdk.platform_factory(
    host="platform.itential.dev",
    user="admin@pronghorn",
    password="your-password"
)

res = platform.get("/health/server")
print(res.json())
```

### Platform — OAuth (client credentials)

```python
import ipsdk

platform = ipsdk.platform_factory(
    host="platform.itential.dev",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

res = platform.get("/adapters")
```

### Gateway

```python
import ipsdk

gateway = ipsdk.gateway_factory(
    host="gateway.itential.dev",
    user="admin@itential",
    password="your-password"
)

res = gateway.get("/devices")
```

### Async

Pass `want_async=True` to get an async client:

```python
import asyncio
import ipsdk

async def main():
    platform = ipsdk.platform_factory(
        host="platform.itential.dev",
        client_id="your-client-id",
        client_secret="your-client-secret",
        want_async=True
    )
    res = await platform.get("/adapters")
    print(res.json())

asyncio.run(main())
```

## HTTP Methods

All clients support `get`, `post`, `put`, `delete`, and `patch`.

| Argument | `get`    | `post`   | `put`    | `delete` | `patch`  |
|----------|----------|----------|----------|----------|----------|
| `path`   | required | required | required | required | required |
| `params` | optional | optional | optional | optional | optional |
| `json`   | —        | optional | optional | —        | optional |

`path` is the relative URI appended to the base URL. `params` is a `dict` serialized to a query string. `json` accepts a `list` or `dict`; when provided, sets `Content-Type: application/json` automatically.

**Base URLs:**
- Platform: `https://host:port`
- Gateway: `https://host:port/api/v2.0`

## Configuration

| Parameter       | `platform_factory` | `gateway_factory` | Description                                      |
|-----------------|--------------------|-------------------|--------------------------------------------------|
| `host`          | `"localhost"`      | `"localhost"`     | Hostname or IP                                   |
| `port`          | `0`                | `0`               | Port; `0` = auto (443 for TLS, 80 for plain HTTP)|
| `use_tls`       | `True`             | `True`            | Use HTTPS                                        |
| `verify`        | `True`             | `True`            | Verify TLS certificates                          |
| `user`          | `"admin"`          | `"admin@itential"`| Username for basic auth                          |
| `password`      | `"admin"`          | `"admin"`         | Password for basic auth                          |
| `client_id`     | `None`             | —                 | OAuth client ID (Platform only)                  |
| `client_secret` | `None`             | —                 | OAuth client secret (Platform only)              |
| `timeout`       | `30`               | `30`              | Request timeout in seconds                       |
| `ttl`           | `0`                | `0`               | Re-authenticate after N seconds; `0` = disabled  |
| `want_async`    | `False`            | `False`           | Return an async client                           |

## Logging

```python
import ipsdk

ipsdk.logging.set_level(ipsdk.logging.DEBUG)
ipsdk.logging.info("Connected to platform")
```

Available levels: `TRACE` (5), `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `FATAL` (90), `NONE` (100).

The `@ipsdk.logging.trace` decorator logs function entry/exit with timing. Sensitive data filtering (PII, passwords, tokens) is enabled by default and can be extended:

```python
ipsdk.logging.add_sensitive_data_pattern("ssn", r"\d{3}-\d{2}-\d{4}")
```

## Development

```bash
# Install dependencies
uv sync

# Run checks (lint, format, security, tests, license headers)
make ci

# Individual targets
make test        # pytest
make coverage    # pytest --cov (100% required)
make lint        # ruff check
make format      # ruff format
make security    # bandit scan
make license     # check GPL headers

# Test across Python 3.10–3.15
uv run tox -p auto
```

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
