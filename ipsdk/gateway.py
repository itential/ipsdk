# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import traceback

from . import connection
from . import logger


def _make_path() -> str:
    """
    Utility function that returns the login url

    Returns:
        A string that provides the login url
    """
    return "/login"


def _make_body(user: str, password: str) -> dict:
    """
    Utility function to make the authentication body used to authenticate to
    the server

    Args:
        user (str): The username to use when authenticating
        password (str): The password to use when authenticating

    Returns:
        A dict object that can be used to send in the body of the
            authentication request
    """
    return {"username": user, "password": password}


def _make_headers() -> dict:
    """
    Utility function that returns a dict object of headers

    Returns:
        A dict object that can be passed to a request to set the headers
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


class AuthMixin(object):
    """
    Authorization mixin for authenticating to Itential Automation Gateway
    """

    def authenticate(self) -> None:
        """
        Provides the authentication function for authenticating to the server
        """
        data = _make_body(self.user, self.password)
        headers = _make_headers()
        path = _make_path()

        try:
            self.client.post(path, headers=headers, json=data)
        except Exception:
            logger.error(traceback.format_exc())


class AsyncAuthMixin(object):
    """
    Async authorization mixin for authenticating to Itential Automation Gateway
    """

    async def authenticate(self):
        """
        Provides the authentication function for authenticating to the server
        """
        data = _make_body(self.user, self.password)
        headers = _make_headers()
        path = _make_path()

        try:
            await self.client.post(path, headers=headers, json=data)
        except Exception:
            logger.error(traceback.format_exc())


Gateway = type("Gateway", (AuthMixin, connection.Connection), {})
AsyncGateway = type("AsyncGateway", (AsyncAuthMixin, connection.AsyncConnection), {})


def gateway_factory(
    host: str="localhost",
    port: int=0,
    use_tls: bool=True,
    verify: bool=True,
    user: str="admin@itential",
    password: str="admin",
    timeout: int=30,
    want_async: bool=False,
):
    """ Create a new instance of a Gateway connection.

    This factory function initializes a Gateway connection using provided parameters or
    environment variable overrides. Uses basic username/password authentication.

    Args:
        host (str): The target host for the connection. The default value for host
            is `admin@itential`

        port (int): Port number to use when connecting to the server.  The default
            value for port is `0`.  When the port value is set to 0, it will be
            automatically determined based  on the value of `use_tls`

        use_tls (bool): Whether to use TLS for the connection.  When this value is
            set to True, TLS will be enabled on the connection and when this value
            is set to False, TLS will be disabled.  The default value is True

        verify (bool): Whether to verify SSL certificates.  When this value is set
            to True, certificates will be verified when connecting to the server and
            when this value is set to False, certificate verification will be
            disabled.  The default value is True.

        user (str): The username to use when authenticating to the server.  The
            default value is `admin@itential`

        password (str): The password to use when authenticating to the server.  The
            default value is `admin`

        timeout (int): Timeout for the connection, in seconds.

        want_async (bool): When set to True, the factory function will return
            an async connection object and when set to False the factory will
            return a connection object.

    Returns:
        An initialized connection instance
    """

    factory = AsyncGateway if want_async is True else Gateway
    return factory(
        host=host,
        port=port,
        use_tls=use_tls,
        verify=verify,
        user=user,
        password=password,
        timeout=timeout,
        base_path="/api/v2.0",
    )
