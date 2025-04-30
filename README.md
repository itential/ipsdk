# ipsdk

The Itential Python SDK provides a client implementation in Python for writing
scripts that can make API calls Itential Platform, Itential Automation Gateway
4.x or Itential Cloud.

## Features

- Easy API requests with automatic authentication
- Support for OAuth and user/password login
- Customizable connection settings
- Centralized logging configuration

## Usage

The `ipsdk` package provides factory functions for connecting to either
Itential Platform or Itential Automation Gateway.

The `platform_factory(...)` function creates a connection to Itential Platform
The `gateway_factory(...)` function creates a connection to Itential Automation Gateway

The below example demonstrates conencting to Itential Platform using the
factory function.

```python
import ipsdk

# Create a connection to Itential Platform
platform = ipsdk.platform_factory(
    host="platform.itential.com",
    user="admin@pronghorn",
    password="admin"
)

# Set a GET request to the server
res = platform.get("/whoami")

# Print the response information to stdout
print(res.status_code, res.body)
```

## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
