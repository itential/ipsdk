# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any
from typing import Optional

import httpx

from . import connection
from . import exceptions
from . import jsonutils
from . import logging


def _make_oauth_headers() -> dict[str, str]:
    return {"Content-Type": "application/x-www-form-urlencoded"}


def _make_oauth_path() -> str:
    return "/oauth/token"


def _make_oauth_body(client_id: str, client_secret: str) -> dict[str, str]:
    return {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }


def _make_basicauth_body(user: str, password: str) -> dict[str, dict[str, str]]:
    return {
        "user": {
            "username": user,
            "password": password,
        }
    }


def _make_basicauth_path() -> str:
    return "/login"


class AuthMixin:
    """
    Authorization mixin for authenticating to Itential Platform.
    """

    # Attributes that should be provided by ConnectionBase
    user: Optional[str]
    password: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    client: httpx.Client
    token: Optional[str]

    def authenticate(self) -> None:
        """
        Provides the authentication function for authenticating to the server
        """
        if self.client_id is not None and self.client_secret is not None:
            self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            self.authenticate_user()
        else:
            msg = (
                "No valid authentication credentials provided. "
                "Required: (client_id + client_secret) or (user + password)"
            )
            raise exceptions.IpsdkError(msg)

        logging.info("client connection successfully authenticated")

    def authenticate_user(self) -> None:
        """
        Performs authentication for basic authorization
        """
        logging.info("Attempting to perform basic authentication")

        assert self.user is not None
        assert self.password is not None
        data = _make_basicauth_body(self.user, self.password)
        path = _make_basicauth_path()

        try:
            res = self.client.post(path, json=data)
            res.raise_for_status()

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc.message, exc)

        except httpx.RequestError as exc:
            logging.exception(exc.message, exc)
            raise exceptions.RequestError(exc.message, exc)

    def authenticate_oauth(self) -> None:
        """
        Performs authentication for OAuth client credentials
        """
        logging.info("Attempting to perform oauth authentication")

        assert self.client_id is not None
        assert self.client_secret is not None
        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _make_oauth_headers()
        path = _make_oauth_path()

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
            raise exceptions.HTTPStatusError(exc.message, exc)

        except httpx.RequestError as exc:
            logging.exception(exc.message, exc)
            raise exceptions.RequestError(exc.message, exc)


class AsyncAuthMixin:
    """
    Platform is a HTTP connection to Itential Platform
    """

    # Attributes that should be provided by ConnectionBase
    user: Optional[str]
    password: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    client: httpx.AsyncClient
    token: Optional[str]

    async def authenticate(self) -> None:
        """
        Provides the authentication function for authenticating to the server
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

    async def authenticate_basicauth(self) -> None:
        """
        Performs authentication for basic authorization
        """
        logging.info("Attempting to perform basic authentication")

        assert self.user is not None
        assert self.password is not None
        data = _make_basicauth_body(self.user, self.password)
        path = _make_basicauth_path()

        try:
            res = await self.client.post(path, json=data)
            res.raise_for_status()

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc.message, exc)

        except httpx.RequestError as exc:
            logging.exception(exc.message, exc)
            raise exceptions.RequestError(exc.message, exc)

    async def authenticate_oauth(self) -> None:
        """
        Performs authentication for OAuth client credentials
        """
        logging.info("Attempting to perform oauth authentication")

        assert self.client_id is not None
        assert self.client_secret is not None
        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _make_oauth_headers()
        path = _make_oauth_path()

        try:
            res = await self.client.post(path, headers=headers, data=data)
            res.raise_for_status()

        except httpx.HTTPStatusError as exc:
            logging.exception(exc)
            raise exceptions.HTTPStatusError(exc.message, exc)

        except httpx.RequestError as exc:
            logging.exception(exc.message, exc)
            raise exceptions.RequestError(exc.message, exc)


# Define type aliases for the dynamically created classes
Platform = type("Platform", (AuthMixin, connection.Connection), {})
AsyncPlatform = type("AsyncPlatform", (AsyncAuthMixin, connection.AsyncConnection), {})

# Type aliases for mypy
PlatformType = Platform
AsyncPlatformType = AsyncPlatform


def platform_factory(
    host: str = "localhost",
    port: int = 0,
    use_tls: bool = True,
    verify: bool = True,
    user: str = "admin",
    password: str = "admin",
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    timeout: int = 30,
    want_async: bool = False,
) -> Any:
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

        want_async (bool): When set to True, the factory function will return
            an async connection object and when set to False the factory will
            return a connection object.

    Returns:
        Platform: An initialized Platform connection instance.
    """

    factory = AsyncPlatform if want_async is True else Platform
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
    )
