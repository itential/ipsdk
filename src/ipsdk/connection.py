# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

"""HTTP connection implementations for the Itential Python SDK.

This module provides both synchronous and asynchronous HTTP client implementations
for communicating with Itential Platform and Itential Automation Gateway. The
connection classes handle request building, authentication, error handling, and
response processing.

Architecture
------------
The module uses an abstract base class pattern with three main classes:

ConnectionBase:
    Abstract base class that provides shared functionality for both sync and async
    connections. Handles URL construction, request building, parameter validation,
    and common configuration options (TLS, verification, timeouts, authentication).

Connection:
    Synchronous HTTP client implementation using httpx.Client. Provides blocking
    HTTP methods (GET, POST, PUT, PATCH, DELETE) for making API requests. Supports
    automatic authentication on first request and comprehensive error handling.

AsyncConnection:
    Asynchronous HTTP client implementation using httpx.AsyncClient. Provides
    async/await-based HTTP methods for non-blocking API requests. Mirrors the
    functionality of Connection but with async support.

Key Features
------------
- Automatic URL construction from host, port, base_path, and TLS settings
- Request building with automatic JSON Content-Type and Accept headers
- Built-in authentication flow that triggers on first request
- Bearer token support for OAuth authentication
- Comprehensive error handling with SDK-specific exceptions
- Support for query parameters and JSON request bodies
- Custom User-Agent header with SDK version information
- Request validation for method, path, params, and JSON body
- Full support for all standard HTTP methods

HTTP Methods
------------
Both Connection and AsyncConnection support the following HTTP methods:

- GET: Retrieve resources (no request body)
- POST: Create resources or submit data (with JSON body support)
- PUT: Update/replace resources (with JSON body support)
- PATCH: Partially update resources (with JSON body support)
- DELETE: Delete resources (no request body)

Authentication
--------------
The connection classes work with authentication mixins from the platform and
gateway modules to handle different authentication schemes:

- OAuth client credentials (Platform)
- Basic username/password authentication (Platform and Gateway)

Authentication is performed automatically on the first API request. Subsequent
requests use the authentication token or session established during the initial
authentication.

Error Handling
--------------
All HTTP operations raise SDK-specific exceptions for consistent error handling:

- RequestError: Network-level errors (connection refused, timeouts, DNS failures)
- HTTPStatusError: HTTP error responses (4xx, 5xx status codes)
- IpsdkError: General SDK errors (invalid parameters, configuration issues)

Examples
--------
The connection classes are typically not instantiated directly but through
factory functions::

    from ipsdk import platform_factory

    # Factory creates and configures Connection instance
    platform = platform_factory(
        host="platform.example.com",
        port=443,
        use_tls=True,
        verify=True,
        timeout=30
    )

    # Make API requests (authentication happens automatically)
    response = platform.get("/api/v2.0/workflows")
    print(response.json())

Async usage::

    from ipsdk import gateway_factory

    # Factory creates AsyncConnection instance
    gateway = gateway_factory(
        host="gateway.example.com",
        want_async=True
    )

    # Use async/await for requests
    async def fetch_devices():
        response = await gateway.get("/devices")
        return response.json()

Direct instantiation (advanced)::

    from ipsdk.connection import Connection

    # Create connection manually
    conn = Connection(
        host="api.example.com",
        port=443,
        base_path="/api/v2.0",
        use_tls=True,
        verify=True,
        user="admin",
        password="password",
        timeout=30
    )

    # Must implement authenticate() method via mixin
    # conn.authenticate() will be called automatically
"""

import abc
import asyncio
import threading
import time
import urllib.parse

from typing import Any

import httpx

from . import exceptions
from . import logging
from . import metadata
from .http import HTTPMethod
from .http import Response


class ConnectionBase:
    client: httpx.Client | httpx.AsyncClient

    @logging.trace
    def __init__(
        self,
        host: str,
        port: int = 0,
        base_path: str | None = None,
        use_tls: bool = True,
        verify: bool = True,
        user: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int = 30,
        ttl: int = 0,
    ) -> None:
        """Initialize the base connection class.

        ConnectionBase is the base connection type that all connection classes
        are derived from. It provides common properties used by both sync and
        async connection types.

        Args:
            host: Hostname or IP address to connect to.
            port: Port value for API connection. If 0, auto-determined based on
                use_tls (443 for TLS, 80 for non-TLS). Defaults to 0.
            base_path: Base URL path prepended to requests. Should not include
                hostname or port. Defaults to None.
            use_tls: Enable TLS for the connection. Defaults to True.
            verify: Enable certificate verification. Defaults to True.
            user: Username for server authentication. Defaults to None.
            password: Password for server authentication. Defaults to None.
            client_id: Client ID for OAuth authentication. Defaults to None.
            client_secret: Client secret for OAuth authentication. Defaults to None.
            timeout: Request timeout in seconds. Defaults to 30.
            ttl: Time to live in seconds before forcing reauthentication. If 0,
                reauthentication is disabled. Defaults to 0.

        Returns:
            None

        Raises:
            None
        """
        self.user = user
        self.password = password

        self.client_id = client_id
        self.client_secret = client_secret

        self.token = None

        self.authenticated = False
        self._auth_lock: Any | None = None
        self._auth_timestamp: float | None = None
        self.ttl = ttl

        self.client = self.__init_client__(
            base_url=self._make_base_url(host, port, base_path, use_tls),
            verify=verify,
            timeout=timeout,
        )
        self.client.headers["User-Agent"] = f"ipsdk/{metadata.version}"

    @logging.trace
    def _make_base_url(
        self,
        host: str,
        port: int = 0,
        base_path: str | None = None,
        use_tls: bool = True,
    ) -> str:
        """Construct a valid base URL from individual components.

        Joins the host, port, base path, and protocol to create the full base
        URL for API requests.

        Args:
            host: Hostname or IP address of the API endpoint.
            port: Port for API connection. If 0, auto-determined based on use_tls
                (443 for TLS, 80 for non-TLS). Defaults to 0.
            base_path: Base path to prepend to the URL. Defaults to None.
            use_tls: Enable TLS (https). Defaults to True.

        Returns:
            str: The constructed base URL.

        Raises:
            None
        """
        if port == 0:
            port = 443 if use_tls is True else 80

        if port not in (None, 80, 443):
            host = f"{host}:{port}"

        base_path = "" if base_path is None else base_path
        proto = "https" if use_tls is True else "http"

        return urllib.parse.urlunsplit((proto, host, base_path, None, None))

    @logging.trace
    def _build_request(
        self,
        method: HTTPMethod,
        path: str,
        json: str | bytes | dict | list | None = None,
        params: dict[str, Any | None] | None = None,
    ) -> httpx.Request:
        """Build an HTTP request object.

        Creates an httpx.Request with the specified method, path, parameters,
        and JSON body. Automatically sets Content-Type and Accept headers to
        application/json when json data is provided.

        Args:
            method: HTTP method for the request.
            path: Resource path appended to the base URL.
            json: JSON body data. If dict or list, automatically serialized.
                Defaults to None.
            params: Query string parameters. Defaults to None.

        Returns:
            httpx.Request: The constructed request object ready to send.

        Raises:
            None
        """
        self._validate_request_args(method, path, params, json)

        headers = {}

        # If the value of json is not None, automatically set the Content-Type
        # and Accept headers to "application/json".  Technically, httpx will do
        # this for us but setting it here to make it very explicit.
        if json is not None:
            logging.debug("Setting Content-Type and Accept headers due to json data")
            headers.update(
                {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

        if self.token is not None:
            logging.debug("Adding Authorization header to request")
            headers["Authorization"] = f"Bearer {self.token}"

        # The value for the keyword `json` is passed to the httpx build_request
        # function.  If the value is of type list or dict, it will
        # automatically be dumped to a string value and inserted into the body
        # of the request.
        return self.client.build_request(
            method=method.value,
            url=path,
            params=params,
            headers=headers,
            json=json,
        )

    @logging.trace
    def _validate_request_args(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | (list | None) = None,
    ) -> None:
        """
        Validate request arguments to ensure they have correct types.

        This method validates that all request parameters conform to expected
        types before building and sending the HTTP request. It checks that the
        method is a valid HTTPMethod enum, params is a dict if provided, json
        is a dict or list if provided, and path is a string.

        Args:
            method (HTTPMethod): The HTTP method enum value to validate
            path (str): The request path to validate
            params (dict[str, Any | None]): Query parameters dict to validate
            json (Union[str, bytes, dict, list | None]): JSON body to validate

        Returns:
            None

        Raises:
            IpsdkError: If method is not HTTPMethod type, params is not dict,
                json is not dict/list, or path is not string
        """
        if isinstance(method, HTTPMethod) is False:
            msg = "method must be of type `HTTPMethod`"
            raise exceptions.IpsdkError(msg)

        if all((params is not None, isinstance(params, dict) is False)):
            msg = "params must be of type `dict`"
            raise exceptions.IpsdkError(msg)

        if all((json is not None, isinstance(json, (list, dict)) is False)):
            msg = "json must be of type `dict` or `list`"
            raise exceptions.IpsdkError(msg)

        if isinstance(path, str) is False:
            msg = "path must be of type `str`"
            raise exceptions.IpsdkError(msg)

    @logging.trace
    def _needs_reauthentication(self) -> bool:
        """Check if reauthentication is needed based on timeout.

        Determines whether the connection needs to reauthenticate by checking
        if the ttl (time to live) has been exceeded since the last authentication.
        If ttl is 0 (disabled) or no authentication has occurred yet,
        returns False.

        Args:
            None

        Returns:
            bool: True if reauthentication is needed, False otherwise.

        Raises:
            None
        """
        if self.ttl <= 0:
            return False

        if self._auth_timestamp is None:
            return False

        elapsed = time.time() - self._auth_timestamp
        if elapsed >= self.ttl:
            logging.info(
                f"Auth TTL exceeded ({elapsed:.1f}s >= {self.ttl}s)"
            )
            return True

        return False

    @abc.abstractmethod
    def __init_client__(
        self, base_url: str | None = None, verify: bool = True, timeout: int = 30
    ) -> httpx.Client | httpx.AsyncClient:
        """Initialize the HTTP client.

        Abstract method to be implemented by subclasses to create either a
        synchronous or asynchronous HTTP client.

        Args:
            base_url: Base URL prepended to all requests. Defaults to None.
            verify: Enable certificate verification. Defaults to True.
            timeout: Connection timeout in seconds. Defaults to 30.

        Returns:
            httpx.Client | httpx.AsyncClient: The initialized HTTP client.

        Raises:
            None
        """


class Connection(ConnectionBase):
    client: httpx.Client  # Override the Union type from base class

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._auth_lock = threading.Lock()

    @logging.trace
    def __init_client__(
        self, base_url: str | None = None, verify: bool = True, timeout: int = 30
    ) -> httpx.Client:
        """Initialize the synchronous HTTP client.

        Creates an httpx.Client instance for making synchronous HTTP requests
        to the server.

        Args:
            base_url: Base URL prepended to all requests. Defaults to None.
            verify: Enable certificate validation for TLS connections. Defaults to True.
            timeout: Connection timeout in seconds. Defaults to 30.

        Returns:
            httpx.Client: The initialized synchronous HTTP client.

        Raises:
            None
        """
        logging.info(f"Creating new client for {base_url}")
        return httpx.Client(
            base_url=base_url or "",
            verify=verify,
            timeout=timeout,
        )

    @abc.abstractmethod
    def authenticate(self) -> None:
        """
        Abstract method for implementing authentication
        """

    @logging.trace
    def _send_request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Response:
        """Send an HTTP request to the API endpoint.

        Automatically handles authentication on first request. Sets Content-Type
        and Accept headers to application/json when JSON body is provided.
        Supports automatic reauthentication based on ttl setting.

        Args:
            method: HTTP method for the request.
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.
            json: JSON payload for request body. If dict or list, automatically
                serialized. Defaults to None.

        Returns:
            Response: The HTTP response wrapped in a Response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        # Check if reauthentication is needed due to timeout
        if self._needs_reauthentication():
            logging.info("Forcing reauthentication due to timeout")
            self.authenticated = False
            self.token = None

        if self.authenticated is False:
            assert self._auth_lock is not None
            with self._auth_lock:
                if self.authenticated is False:
                    self.authenticate()
                    self.authenticated = True
                    self._auth_timestamp = time.time()

        request = self._build_request(
            method=method,
            path=path,
            params=params,
            json=json,
        )

        try:
            logging.info(f"{method.value} {path}")
            res = self.client.send(request)
            res.raise_for_status()

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except Exception as exc:
            logging.exception(exc)
            raise

        return Response(res)

    @logging.trace
    def get(self, path: str, params: dict[str, Any | None] | None = None) -> Response:
        """Send an HTTP GET request to the server.

        Args:
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.

        Returns:
            Response: The HTTP response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        return self._send_request(HTTPMethod.GET, path=path, params=params)

    @logging.trace
    def delete(
        self, path: str, params: dict[str, Any | None] | None = None
    ) -> Response:
        """Send an HTTP DELETE request to the server.

        Args:
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.

        Returns:
            Response: The HTTP response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        return self._send_request(HTTPMethod.DELETE, path=path, params=params)

    @logging.trace
    def post(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | list | dict | None = None,
    ) -> Response:
        """Send an HTTP POST request to the server.

        Args:
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.
            json: JSON payload for request body. If dict or list, automatically
                serialized. Defaults to None.

        Returns:
            Response: The HTTP response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        return self._send_request(HTTPMethod.POST, path=path, params=params, json=json)

    @logging.trace
    def put(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | list | dict | None = None,
    ) -> Response:
        """Send an HTTP PUT request to the server.

        Args:
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.
            json: JSON payload for request body. If dict or list, automatically
                serialized. Defaults to None.

        Returns:
            Response: The HTTP response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        return self._send_request(HTTPMethod.PUT, path=path, params=params, json=json)

    @logging.trace
    def patch(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | list | dict | None = None,
    ) -> Response:
        """Send an HTTP PATCH request to the server.

        Args:
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.
            json: JSON payload for request body. If dict or list, automatically
                serialized. Defaults to None.

        Returns:
            Response: The HTTP response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        return self._send_request(HTTPMethod.PATCH, path=path, params=params, json=json)


class AsyncConnection(ConnectionBase):
    client: httpx.AsyncClient  # Override the Union type from base class

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._auth_lock = asyncio.Lock()

    @logging.trace
    def __init_client__(
        self, base_url: str | None = None, verify: bool = True, timeout: int = 30
    ) -> httpx.AsyncClient:
        """
        Initialize the httpx.AsyncClient instance

        The `httpx.AsyncClient` instance provides the connection to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.

        Args:
            base_url (str): The base URL used to prepend to every request

            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

            timeout (int): Set the connection timeout value to be used for
                each request in seconds.  The default value is 30.

        Returns:
            An instance of `httpx.AsyncClient`
        """
        logging.info(f"Creating new async client for {base_url}")
        return httpx.AsyncClient(
            base_url=base_url or "", verify=verify, timeout=timeout
        )

    @abc.abstractmethod
    async def authenticate(self) -> None:
        """
        Abstract method for implementing authentication
        """

    @logging.trace
    async def _send_request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Response:
        """Send an asynchronous HTTP request to the API endpoint.

        Automatically handles authentication on first request. Sets Content-Type
        and Accept headers to application/json when JSON body is provided.
        Supports automatic reauthentication based on ttl setting.

        Args:
            method: HTTP method for the request.
            path: URI path combined with base_url to form the full resource URL.
            params: Query string parameters. Defaults to None.
            json: JSON payload for request body. If dict or list, automatically
                serialized. Defaults to None.

        Returns:
            Response: The HTTP response wrapped in a Response object.

        Raises:
            RequestError: Network or connection errors occurred.
            HTTPStatusError: Server returned an HTTP error status (4xx, 5xx).
        """
        # Check if reauthentication is needed due to timeout
        if self._needs_reauthentication():
            logging.info("Forcing reauthentication due to timeout")
            self.authenticated = False
            self.token = None

        if self.authenticated is False:
            assert self._auth_lock is not None
            async with self._auth_lock:
                if self.authenticated is False:
                    await self.authenticate()
                    self.authenticated = True
                    self._auth_timestamp = time.time()

        request = self._build_request(
            method=method,
            path=path,
            params=params,
            json=json,
        )

        try:
            logging.info(f"{method.value} {path}")
            res = await self.client.send(request)
            res.raise_for_status()

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except Exception as exc:
            logging.exception(exc)
            raise

        return Response(res)

    @logging.trace
    async def get(
        self, path: str, params: dict[str, Any | None] | None = None
    ) -> Response:
        """
        Send a HTTP GET request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return await self._send_request(HTTPMethod.GET, path=path, params=params)

    @logging.trace
    async def delete(
        self, path: str, params: dict[str, Any | None] | None = None
    ) -> Response:
        """
        Send a HTTP DELETE request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return await self._send_request(HTTPMethod.DELETE, path=path, params=params)

    @logging.trace
    async def post(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Response:
        """
        Send a HTTP POST request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.POST, path=path, params=params, json=json
        )

    @logging.trace
    async def put(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Response:
        """
        Send a HTTP PUT request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.PUT, path=path, params=params, json=json
        )

    @logging.trace
    async def patch(
        self,
        path: str,
        params: dict[str, Any | None] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Response:
        """
        Send a HTTP PATCH request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.PATCH, path=path, params=params, json=json
        )
