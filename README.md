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

The `ipsdk` package provides three factory functions for connecting to
different types of servers.

The `platform()` function creates a connection to Itential Platform
The `gateway()` function creates a connection to Itential Automation Gateway
The `cloud()` function creates a connection to Itential Automation Service

The below example demonstrates conencting to Itential Platform using the
factory function.

```python
import ipsdk

# Create a connection to Itential Platform
server = ipsdk.platform(
    host="platform.itential.com",
    user="admin@pronghorn",
    password="admin"
)

# Set a GET request to the server
res = server.get("/whoami")

# Print the response information to stdout
print(res.status_code, res.body)
```

Different functions provide different configuation options.

##  Configuration via Environment Variables

You can set constructor parameters using the following environment variables:

| Variable                 | Description               | Platform  | Gateway   | Cloud     |
|--------------------------|---------------------------|-----------|-----------|-----------|
| `ITENTIAL_HOST`          | API host                  | supported | supported | supported |
| `ITENTIAL_PORT`          | API port                  | supported | supported | supported |
| `ITENTIAL_USE_TLS`       | Use TLS (true/false)      | supported | supported | supported |
| `ITENTIAL_VERIFY`        | SSL verify (true/false)   | supported | supported | supported |
| `ITENTIAL_TIMEOUT`       | Request timeout (seconds) | supported | supported | supported |
| `ITENTIAL_USER`          | Username                  | supported | supported | n/a       |
| `ITENTIAL_PASSWORD`      | Password                  | supported | supported | n/a       |
| `ITENTIAL_CLIENT_ID`     | OAuth client ID           | supported | supported | supported |
| `ITENTIAL_CLIENT_SECRET` | OAuth client secret       | supported | supported | supported |


## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
