# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import traceback

from . import jsonutils
from . import connection
from . import logger

def _make_oauth_headers() -> dict:
    return {"Content-Type": "application/x-www-form-urlencoded"}


def _make_oauth_path() -> str:
    return "/oauth/token"


def _make_oauth_body(client_id: str, client_secret: str) -> dict:
    return {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }


def _make_basicauth_body(user: str, password: str) -> dict:
    return {
        "user": {
            "username": user,
            "password": password,
        }
    }


def _make_basicauth_path() -> str:
    return "/login"


class AuthMixin(object):
    """
    Authoriztion mixin for authenticating to Itential Platform.
    """

    def authenticate(self) -> None:
        """
        Provides the authentication function for authenticating to the server
        """
        if self.client_id is not None and self.client_secret is not None:
            self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            self.authenticate_user()
        else:
            raise ValueError("no authentication methods left to try")
        logger.info("client connection successfully authenticated")

    def authenticate_user(self) -> None:
        """
        Performs authentication for basic authorization
        """
        logger.info("Attempting to perform basic authentication")

        data = _make_basicauth_body(self.user, self.password)
        path = _make_basicauth_path()

        try:
            res = self.client.post(path, json=data)
            res.raise_for_status()
        except Exception:
            logger.error(traceback.format_exc())
            raise


    def authenticate_oauth(self) -> None:
        """
        Performs authentication for OAuth client credentials
        """
        logger.info("Attempting to perform oauth authentication")

        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _make_oauth_headers()
        path = _make_oauth_path()

        try:
            res = self.client.post(path, headers=headers, data=data)
            self.token =  jsonutils.loads(res.text).get("access_token")
        except Exception:
            logger.error(traceback.format_exc())
            raise


class AsyncAuthMixin(object):
    """
    Platform is a HTTP connection to Itential Platform
    """

    async def authenticate(self):
        """
        Provides the authentication function for authenticating to the server
        """
        if self.client_id is not None and self.client_secret is not None:
            await self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            await self.authenticate_basicauth()
        else:
            raise ValueError("no authentication methods left to try")
        logger.info("client connection successfully authenticated")

    async def authenticate_basicauth(self):
        """
        Performs authentication for basic authorization
        """
        logger.info("Attempting to perform basic authentication")

        data = _make_basicauth_body(self.user, self.password)
        path = _make_basicauth_path()

        try:
            res = await self.client.post(path, json=data)
            res.raise_for_status()
        except Exception:
            logger.error(traceback.format_exc())
            raise


    async def authenticate_oauth(self):
        """
        Performs authentication for OAuth client credentials
        """
        logger.info("Attempting to perform oauth authentication")

        data = _make_oauth_body(self.client_id, self.client_secret)
        headers = _make_oauth_headers()
        path = _make_oauth_path()

        try:
            res = await self.client.post(path, headers=headers, data=data)
            self.token =  jsonutils.loads(res.text).get("access_token")
        except Exception:
            logger.error(traceback.format_exc())
            raise



Platform = type("Platform", (AuthMixin, connection.Connection), {})
AsyncPlatform = type("AsyncPlatform", (AsyncAuthMixin, connection.AsyncConnection), {})


def platform_factory(
    host: str="localhost",
    port: int=0,
    use_tls: bool=True,
    verify: bool=True,
    user: str="admin",
    password: str="admin",
    client_id: str=None,
    client_secret: str=None,
    timeout: int=30,
    want_async: bool=False,
):
    """
    Create a new instance of a Platform connection.

    This factory function initializes a Platform connection using provided parameters or
    environment variable overrides. Supports both user/password and client credentials.

    Args:
        host (str): The target host for the connection.  The default value for
            host is `loclahost`

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

        user (str): The username to ues when authenticating to the server.  The
            default value is `admin`

        password (str): The password to use when authenticaing to the server.  The
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
