# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

"""Itential Platform client implementation for the SDK.

This module provides client implementations for connecting to and interacting
with Itential Platform. It includes both synchronous and asynchronous clients
with support for OAuth (client credentials) and basic username/password
authentication.

Components
----------
The module exports the following components:

platform_factory:
    Factory function that creates and configures Platform or AsyncPlatform
    instances based on the want_async parameter. This is the primary
    entry point for creating Platform connections.

Platform:
    Synchronous client for Itential Platform. Dynamically created by
    combining AuthMixin with Connection base class. Supports all standard
    HTTP methods (GET, POST, PUT, PATCH, DELETE) with automatic authentication
    using either OAuth or basic auth.

AsyncPlatform:
    Asynchronous client for Itential Platform. Dynamically created by
    combining AsyncAuthMixin with AsyncConnection base class. Provides
    async/await support for non-blocking API requests with OAuth or basic auth.

AuthMixin:
    Synchronous authentication mixin that implements both OAuth client
    credentials and basic username/password authentication for Platform.
    Automatically selects the appropriate authentication method based on
    provided credentials.

AsyncAuthMixin:
    Asynchronous authentication mixin that implements both OAuth and basic
    authentication for Platform with async/await support.

Authentication
--------------
Itential Platform supports two authentication methods:

OAuth Client Credentials (Recommended):
    Uses client_id and client_secret to obtain an access token via the
    OAuth 2.0 client credentials flow. The token is included in subsequent
    requests as a Bearer token in the Authorization header.

    Flow:
    1. Client is created with client_id and client_secret
    2. On first API request, POST to /oauth/token with credentials
    3. Extract access_token from response
    4. Include token in Authorization header for all subsequent requests

Basic Authentication:
    Uses username and password credentials for authentication. Credentials
    are sent to the /login endpoint and a session is maintained for
    subsequent requests.

    Flow:
    1. Client is created with user and password
    2. On first API request, POST to /login with credentials
    3. Session is maintained via cookies for subsequent requests

The authentication method is automatically selected based on which credentials
are provided:
- If client_id and client_secret are provided, OAuth is used
- If user and password are provided, basic auth is used
- If neither pair is complete, IpsdkError is raised

Base URL
--------
The Platform client uses the host as the base URL without any additional
path prefix. All API paths should include the full resource path including
the API version.

For example::

    platform.get("/api/v2.0/workflows")  # Full path required

Supported HTTP Methods
----------------------
All Platform clients support the following HTTP methods:

- GET: Retrieve resources
- POST: Create resources or submit data
- PUT: Update/replace resources
- PATCH: Partially update resources
- DELETE: Delete resources

Error Handling
--------------
All Platform operations may raise the following exceptions:

- RequestError: Network/connection errors (timeouts, connection refused,
  DNS failures)
- HTTPStatusError: HTTP error responses (401 Unauthorized, 404 Not Found,
  500 Internal Server Error, etc.)
- IpsdkError: General SDK errors (invalid parameters, missing/incomplete
  credentials)

Examples
--------
OAuth authentication (recommended)::

    from ipsdk import platform_factory

    # Create Platform client with OAuth
    platform = platform_factory(
        host="platform.example.com",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )

    # Get all workflows
    response = platform.get("/api/v2.0/workflows")
    workflows = response.json()

    # Create a new workflow
    response = platform.post(
        "/api/v2.0/workflows",
        json={"name": "my-workflow", "description": "Test workflow"}
    )
    workflow = response.json()

Basic authentication::

    from ipsdk import platform_factory

    # Create Platform client with basic auth
    platform = platform_factory(
        host="platform.example.com",
        user="admin",
        password="password"
    )

    # Make API requests
    response = platform.get("/api/v2.0/workflows")
    workflows = response.json()

Asynchronous usage::

    from ipsdk import platform_factory

    # Create async Platform client
    platform = platform_factory(
        host="platform.example.com",
        client_id="your-client-id",
        client_secret="your-client-secret",
        want_async=True
    )

    # Use async/await for requests
    async def get_workflows():
        response = await platform.get("/api/v2.0/workflows")
        return response.json()

    async def create_workflow(name):
        response = await platform.post(
            "/api/v2.0/workflows",
            json={"name": name}
        )
        return response.json()

Custom configuration::

    from ipsdk import platform_factory

    # Create Platform with custom settings
    platform = platform_factory(
        host="platform.example.com",
        port=8443,
        use_tls=True,
        verify=True,
        client_id="your-client-id",
        client_secret="your-client-secret",
        timeout=60
    )

Error handling::

    from ipsdk import platform_factory
    from ipsdk.exceptions import HTTPStatusError, RequestError, IpsdkError

    try:
        platform = platform_factory(
            host="platform.example.com",
            client_id="your-client-id",
            client_secret="your-client-secret"
        )
        response = platform.get("/api/v2.0/workflows")
        workflows = response.json()
    except HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code}: {e}")
    except RequestError as e:
        print(f"Network error: {e}")
    except IpsdkError as e:
        print(f"SDK error: {e}")

Working with responses::

    from ipsdk import platform_factory

    platform = platform_factory(host="platform.example.com")

    # Get workflows with query parameters
    response = platform.get(
        "/api/v2.0/workflows",
        params={"limit": 10, "offset": 0}
    )

    # Check response status
    if response.is_success():
        workflows = response.json()
        print(f"Found {len(workflows)} workflows")
    else:
        print(f"Request failed with status {response.status_code}")
"""

import httpx

from . import connection
from . import exceptions
from . import jsonutils
from . import logging

# OAuth constants
_OAUTH_HEADERS: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
_OAUTH_PATH: str = "/oauth/token"

# Basic authentication constants
_BASICAUTH_PATH: str = "/login"


@logging.trace
def _make_oauth_body(client_id: str, client_secret: str) -> dict[str, str]:
    """Create request body for OAuth client credentials authentication.

    Constructs the form data required for OAuth 2.0 client credentials
    grant type. The body includes grant_type, client_id, and client_secret
    which are sent as form-encoded data to the token endpoint.

    Args:
        client_id (str): OAuth client identifier
        client_secret (str): OAuth client secret

    Returns:
        dict[str, str]: Form data dict for OAuth token request
    """
    return {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }


@logging.trace
def _make_basicauth_body(user: str, password: str) -> dict[str, dict[str, str]]:
    """Create request body for basic username/password authentication.

    Constructs the JSON request body required for basic authentication
    to Platform. The body contains a nested user object with username
    and password fields.

    Args:
        user (str): Username for authentication
        password (str): Password for authentication

    Returns:
        dict[str, dict[str, str]]: JSON body dict for basic auth request
    """
    return {
        "user": {
            "username": user,
            "password": password,
        }
    }



class AuthMixin:
    """Authorization mixin for Itential Platform synchronous authentication.

    This mixin provides authentication methods for Platform connections,
    supporting both OAuth 2.0 client credentials and basic username/password
    authentication. It's designed to be mixed with Connection to create
    the Platform class.

    The mixin automatically selects the appropriate authentication method
    based on which credentials are provided:
    - OAuth: Requires client_id and client_secret
    - Basic: Requires user and password

    Attributes:
        user (str | None): Username for basic authentication (from ConnectionBase)
        password (str | None): Password for basic authentication (from ConnectionBase)
        client_id (str | None): OAuth client ID (from ConnectionBase)
        client_secret (str | None): OAuth client secret (from ConnectionBase)
        client (httpx.Client): HTTP client instance for making requests
        token (str | None): Access token for OAuth authentication

    Methods:
        authenticate(): Main authentication entry point
        authenticate_basicauth(): Basic username/password authentication
        authenticate_oauth(): OAuth 2.0 client credentials authentication
    """

    # Attributes that should be provided by ConnectionBase
    user: str | None
    password: str | None
    client_id: str | None
    client_secret: str | None
    client: httpx.Client
    token: str | None

    @logging.trace
    def authenticate(self) -> None:
        """Authenticate to Itential Platform using configured credentials.

        Automatically selects OAuth or basic authentication based on which
        credentials are provided (client_id/client_secret or user/password).
        Authentication is performed on the first API request and the session
        or token is maintained for subsequent requests.

        Returns:
            None

        Raises:
            IpsdkError: If no valid authentication credentials are provided
            HTTPStatusError: If authentication request fails with HTTP error
            RequestError: If authentication request fails due to network error
        """
        if self.client_id is not None and self.client_secret is not None:
            self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            self.authenticate_basicauth()
        else:
            msg = (
                "No valid authentication credentials provided. "
                "Required: (client_id + client_secret) or (user + password)"
            )
            raise exceptions.IpsdkError(msg)

        logging.info("client connection successfully authenticated")

    @logging.trace
    def authenticate_basicauth(self) -> None:
        """Perform basic username/password authentication to Platform.

        Authenticates to Itential Platform using username and password credentials.
        Sends credentials to the /login endpoint and maintains a session via cookies
        for subsequent requests.

        Returns:
            None

        Raises:
            IpsdkError: If username or password is missing
            HTTPStatusError: If server returns HTTP error status (401, 403, etc.)
            RequestError: If network/connection error occurs (timeout, DNS
                failure, etc.)
        """
        logging.info("Attempting to perform basic authentication")

        if self.user is None or self.password is None:
            msg = "Username and password are required for basic authentication"
            raise exceptions.IpsdkError(msg)

        data = _make_basicauth_body(self.user, self.password)
        path = _BASICAUTH_PATH

        try:
            res = self.client.post(path, json=data)
            res.raise_for_status()

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)

    @logging.trace
    def authenticate_oauth(self) -> None:
        """Perform OAuth 2.0 client credentials authentication to Platform.

        Authenticates to Itential Platform using OAuth 2.0 client credentials flow.
        Requests an access token from the /oauth/token endpoint using client_id
        and client_secret. The token is stored in self.token and included in
        subsequent requests as a Bearer token in the Authorization header.

        Returns:
            None

        Raises:
            IpsdkError: If client_id or client_secret is missing
            HTTPStatusError: If server returns HTTP error status (401, 403, etc.)
            RequestError: If network/connection error occurs (timeout, DNS
                failure, etc.)
        """
        logging.info("Attempting to perform oauth authentication")

        if self.client_id is None or self.client_secret is None:
            msg = "Client ID and client secret are required for OAuth authentication"
            raise exceptions.IpsdkError(msg)

        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _OAUTH_HEADERS
        path = _OAUTH_PATH

        try:
            res = self.client.post(path, headers=headers, data=data)
            res.raise_for_status()

            # Parse the response to extract the token
            response_data = jsonutils.loads(res.text)
            if isinstance(response_data, dict):
                access_token = response_data.get("access_token")
            else:
                access_token = None

            self.token = access_token

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)


class AsyncAuthMixin:
    """Authorization mixin for Itential Platform asynchronous authentication.

    This mixin provides async authentication methods for Platform connections,
    supporting both OAuth 2.0 client credentials and basic username/password
    authentication with async/await support. It's designed to be mixed with
    AsyncConnection to create the AsyncPlatform class.

    The mixin automatically selects the appropriate authentication method
    based on which credentials are provided:
    - OAuth: Requires client_id and client_secret
    - Basic: Requires user and password

    Attributes:
        user (str | None): Username for basic authentication (from ConnectionBase)
        password (str | None): Password for basic authentication (from ConnectionBase)
        client_id (str | None): OAuth client ID (from ConnectionBase)
        client_secret (str | None): OAuth client secret (from ConnectionBase)
        client (httpx.AsyncClient): Async HTTP client instance for making requests
        token (str | None): Access token for OAuth authentication

    Methods:
        authenticate(): Main async authentication entry point
        authenticate_basicauth(): Async basic username/password authentication
        authenticate_oauth(): Async OAuth 2.0 client credentials authentication
    """

    # Attributes that should be provided by ConnectionBase
    user: str | None
    password: str | None
    client_id: str | None
    client_secret: str | None
    client: httpx.AsyncClient
    token: str | None

    @logging.trace
    async def authenticate(self) -> None:
        """Asynchronously authenticate to Platform using configured credentials.

        Automatically selects OAuth or basic authentication based on which
        credentials are provided (client_id/client_secret or user/password).
        Authentication is performed on the first API request and the session
        or token is maintained for subsequent requests.

        Returns:
            None

        Raises:
            IpsdkError: If no valid authentication credentials are provided
            HTTPStatusError: If authentication request fails with HTTP error
            RequestError: If authentication request fails due to network error
        """
        if self.client_id is not None and self.client_secret is not None:
            await self.authenticate_oauth()

        elif self.user is not None and self.password is not None:
            await self.authenticate_basicauth()

        else:
            msg = (
                "No valid authentication credentials provided. "
                "Required: (client_id + client_secret) or (user + password)"
            )
            raise exceptions.IpsdkError(msg)

        logging.info("client connection successfully authenticated")

    @logging.trace
    async def authenticate_basicauth(self) -> None:
        """Asynchronously perform basic username/password authentication to Platform.

        Authenticates to Itential Platform using username and password credentials.
        Sends credentials to the /login endpoint and maintains a session via cookies
        for subsequent requests. Uses async/await for non-blocking operation.

        Returns:
            None

        Raises:
            IpsdkError: If username or password is missing
            HTTPStatusError: If server returns HTTP error status (401, 403, etc.)
            RequestError: If network/connection error occurs (timeout, DNS
                failure, etc.)
        """
        logging.info("Attempting to perform basic authentication")

        if self.user is None or self.password is None:
            msg = "Username and password are required for basic authentication"
            raise exceptions.IpsdkError(msg)

        data = _make_basicauth_body(self.user, self.password)
        path = _BASICAUTH_PATH

        try:
            res = await self.client.post(path, json=data)
            res.raise_for_status()

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)

    @logging.trace
    async def authenticate_oauth(self) -> None:
        """Asynchronously perform OAuth 2.0 client credentials authentication.

        Authenticates to Itential Platform using OAuth 2.0 client credentials flow.
        Requests an access token from the /oauth/token endpoint using client_id
        and client_secret. The token is stored in self.token and included in
        subsequent requests as a Bearer token in the Authorization header.
        Uses async/await for non-blocking operation.

        Returns:
            None

        Raises:
            IpsdkError: If client_id or client_secret is missing
            HTTPStatusError: If server returns HTTP error status (401, 403, etc.)
            RequestError: If network/connection error occurs (timeout, DNS
                failure, etc.)
        """
        logging.info("Attempting to perform oauth authentication")

        if self.client_id is None or self.client_secret is None:
            msg = "Client ID and client secret are required for OAuth authentication"
            raise exceptions.IpsdkError(msg)

        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _OAUTH_HEADERS
        path = _OAUTH_PATH

        try:
            res = await self.client.post(path, headers=headers, data=data)
            res.raise_for_status()

            # Parse the response to extract the token
            response_data = jsonutils.loads(res.text)
            if isinstance(response_data, dict):
                access_token = response_data.get("access_token")
            else:
                access_token = None

            self.token = access_token

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc)

        except httpx.RequestError as exc:
            logging.exception(exc)
            raise exceptions.RequestError(exc)


# Define type aliases for the dynamically created classes
Platform = type("Platform", (AuthMixin, connection.Connection), {})
AsyncPlatform = type("AsyncPlatform", (AsyncAuthMixin, connection.AsyncConnection), {})

# Type aliases for mypy
PlatformType = Platform
AsyncPlatformType = AsyncPlatform


@logging.trace
def platform_factory(
    host: str = "localhost",
    port: int = 0,
    use_tls: bool = True,
    verify: bool = True,
    user: str = "admin",
    password: str = "admin",
    client_id: str | None = None,
    client_secret: str | None = None,
    timeout: int = 30,
    ttl: int = 0,
    want_async: bool = False,
) -> Platform | AsyncPlatform:
    """
    Create a new instance of a Platform connection.

    This factory function initializes a Platform connection using provided parameters or
    environment variable overrides. Supports both user/password and client credentials.

    Args:
        host (str): The target host for the connection.  The default value for
            host is `localhost`

        port (int): Port number to connect to.   The default value for port
            is `0`.   When the value is set to `0`, the port will be automatically
            determined based on the value of `use_tls`

        use_tls (bool): Whether to use TLS for the connection.  When this argument
            is set to `True`, TLS will be enabled and when this value is set
            to `False`, TLS will be disabled  The default value is `True`

        verify (bool): Whether to verify SSL certificates.  When this value
            is set to `True`, the connection will attempt to verify the
            certificates and when this value is set to `False` Certificate
            verification will be disabled.  The default value is `True`

        user (str): The username to use when authenticating to the server.  The
            default value is `admin`

        password (str): The password to use when authenticating to the server.  The
            default value is `admin`

        client_id (str): Optional client ID for token-based authentication.  When
            this value is set, the client will attempt to use OAuth to authenticate
            to the server instead of basic auth.   The default value is None

        client_secret (str): Optional client secret for token-based authentication.
            This value works in conjunction with `client_id` to authenticate to the
            server.  The default value is None

        timeout (int): Configures the timeout value for requests sent to the server.
            The default value for timeout is `30`.

        ttl (int): Time to live in seconds before forcing reauthentication. If 0,
            reauthentication is disabled. The default value is `0`.

        want_async (bool): When set to True, the factory function will return
            an async connection object and when set to False the factory will
            return a connection object.

    Returns:
        Platform: An initialized Platform connection instance.
    """
    factory = AsyncPlatform if want_async else Platform
    return factory(
        host=host,
        port=port,
        use_tls=use_tls,
        verify=verify,
        user=user,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        timeout=timeout,
        ttl=ttl,
    )
