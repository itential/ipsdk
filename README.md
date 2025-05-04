# ipsdk

The Itential Python SDK provides a client implementation in Python for writing
scripts that can make API calls Itential Platform or Itential Automation
Gateway 4.x.

## Features

- Easy API requests with automatic authentication
- Support for OAuth and user/password login
- Customizable connection settings
- Centralized logging configuration

## Getting started

Install `ipsdk` using pip:

```python
$ pip install ipsdk
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
well.  The example below demostrates how to connect to the server using an
async connections.

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
- `PATCH` - Sends a HTTP PATCH request to the server and returns the resutls

The following table shows the keyworkd arguments for each HTTP method:

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

The `json` argument accepts the payload to send in the requeset as JSON.  This
argument accepts either a `list` or `dict` object.  When specified, the data
will automatically be converted to a JSON string and the `Content-Type` and
`Accept` headers will be set to `application/json`.

## Configuration

Both the `platform_factory` and `gateway_factory` functions supporting
configuration using keyword arguments.  The table below shows the keyword
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
 | `want_async`    | `False`            | `False`           |

## Logging

By default all logging is turned off for `ipsdk`.  To enable logging to
`stdout`, using the `set_logging_level` function.

```python
>>> import ipsdk
>>> import logging

>>> ipsdk.set_logging_level(logging.DEBUG)

>>> gateway = ipsdk.gateway_factory(host="gateway.itential.dev")
2025-05-04 08:09:58,105: INFO: Creating new client for https://gateway.itential.dev/api/v2.0

>>> res = gateway.get("/devices")
2025-05-04 08:10:12,009: DEBUG: connect_tcp.started host='gateway.itential.dev' port=443 local_address=None timeout=5.0 socket_options=None
2025-05-04 08:10:12,076: DEBUG: connect_tcp.complete return_value=<httpcore._backends.sync.SyncStream object at 0x7fcb6cdcc980>
2025-05-04 08:10:12,076: DEBUG: start_tls.started ssl_context=<ssl.SSLContext object at 0x7fcb6cf22a80> server_hostname='gateway.itential.dev' timeout=5.0
2025-05-04 08:10:12,097: DEBUG: start_tls.complete return_value=<httpcore._backends.sync.SyncStream object at 0x7fcb6cdd4910>
2025-05-04 08:10:12,097: DEBUG: send_request_headers.started request=<Request [b'POST']>
2025-05-04 08:10:12,098: DEBUG: send_request_headers.complete
2025-05-04 08:10:12,098: DEBUG: send_request_body.started request=<Request [b'POST']>
2025-05-04 08:10:12,098: DEBUG: send_request_body.complete
2025-05-04 08:10:12,098: DEBUG: receive_response_headers.started request=<Request [b'POST']>
2025-05-04 08:10:12,231: DEBUG: receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'Date', b'Sun, 04 May 2025 12:10:12 GMT'), (b'Content-Type', b'application/json'), (b'Transfer-Encoding', b'chunked'), (b'Connection', b'keep-alive'), (b'Server', b'cloudflare'), (b'Last-Modified', b'2025-05-04 12:10:12.220779'), (b'Cache-Control', b'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'), (b'Pragma', b'no-cache'), (b'Expires', b'-1'), (b'X-Frame-Options', b'DENY'), (b'X-Xss-Protection', b'1'), (b'X-Content-Type-Options', b'nosniff'), (b'Cf-Cache-Status', b'DYNAMIC'), (b'Content-Encoding', b'gzip'), (b'Set-Cookie', b'AutomationGatewayToken=NzQ3NS42MzM2NTcxMzYyNDg=; HttpOnly; Path=/'), (b'CF-RAY', b'93a7e4c1a9626abf-RDU'), (b'alt-svc', b'h3=":443"; ma=86400')])
2025-05-04 08:10:12,232: INFO: HTTP Request: POST https://gateway.itential.dev/api/v2.0/login "HTTP/1.1 200 OK"
2025-05-04 08:10:12,233: DEBUG: receive_response_body.started request=<Request [b'POST']>
2025-05-04 08:10:12,233: DEBUG: receive_response_body.complete
2025-05-04 08:10:12,233: DEBUG: response_closed.started
2025-05-04 08:10:12,233: DEBUG: response_closed.complete
2025-05-04 08:10:12,235: DEBUG: send_request_headers.started request=<Request [b'GET']>
2025-05-04 08:10:12,235: DEBUG: send_request_headers.complete
2025-05-04 08:10:12,235: DEBUG: send_request_body.started request=<Request [b'GET']>
2025-05-04 08:10:12,235: DEBUG: send_request_body.complete
2025-05-04 08:10:12,236: DEBUG: receive_response_headers.started request=<Request [b'GET']>
2025-05-04 08:10:12,264: DEBUG: receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'Date', b'Sun, 04 May 2025 12:10:12 GMT'), (b'Content-Type', b'application/json'), (b'Transfer-Encoding', b'chunked'), (b'Connection', b'keep-alive'), (b'Server', b'cloudflare'), (b'Last-Modified', b'2025-05-04 12:10:12.253899'), (b'Cache-Control', b'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'), (b'Pragma', b'no-cache'), (b'Expires', b'-1'), (b'X-Frame-Options', b'DENY'), (b'X-Xss-Protection', b'1'), (b'X-Content-Type-Options', b'nosniff'), (b'Cf-Cache-Status', b'DYNAMIC'), (b'Content-Encoding', b'gzip'), (b'CF-RAY', b'93a7e4c279e36abf-RDU'), (b'alt-svc', b'h3=":443"; ma=86400')])
2025-05-04 08:10:12,264: INFO: HTTP Request: GET https://gateway.itential.dev/api/v2.0/devices "HTTP/1.1 200 OK"
2025-05-04 08:10:12,264: DEBUG: receive_response_body.started request=<Request [b'GET']>
2025-05-04 08:10:12,264: DEBUG: receive_response_body.complete
2025-05-04 08:10:12,264: DEBUG: response_closed.started
2025-05-04 08:10:12,265: DEBUG: response_closed.complete

>>> print(res)
<Response [200 OK]>
```

## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
