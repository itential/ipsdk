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

```python
import ipsdk

# Create a connection to Itential Platform
server = ipsdk.client.platform(
    host="platform.itential.com",
    user="admin@pronghorn",
    password="admin"
)

# Set a GET request to the server
res = platform.get("/whoami")

# Print the response information to stdout
print(response.status_code, response.body)
```

##  Configuration via Environment Variables

You can override constructor parameters using the following environment variables:

| Variable                 | Description                     |
|--------------------------|---------------------------------|
| `ITENTIAL_HOST`          | API host                        |
| `ITENTIAL_PORT`          | API port                        |
| `ITENTIAL_USE_TLS`       | Use TLS (true/false)            |
| `ITENTIAL_VERIFY`        | SSL verify (true/false)         |
| `ITENTIAL_TIMEOUT`       | Request timeout (seconds)       |
| `ITENTIAL_USER`          | Username                        |
| `ITENTIAL_PASSWORD`      | Password                        |
| `ITENTIAL_CLIENT_ID`     | OAuth client ID                 |
| `ITENTIAL_CLIENT_SECRET` | OAuth client secret             |



## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
