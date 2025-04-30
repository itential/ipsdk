# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import traceback

from . import jsonutils
from . import http

logger = logging.getLogger(__name__)


class Platform(http.Connection):
    """ Platform is a HTTP connection to Itential Platform
    """

    def __str__(self) -> str:
        """Return the string representation of the object instance
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """Return the string representation of the object instance
        """
        cls = self.__class__.__name__
        return f"{cls}(host={self.host!r})"

    def authenticate(self):
        """Provides the authentication function for authenticating to the server
        """
        if self.client_id is not None and self.client_secret is not None:
            self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            self.authenticate_user()
        else:
            raise ValueError("no authentication methods left to try")
        self.authenticated = True

    def authenticate_user(self):
        """Performs authentication for basic authorization
        """
        data = {
            "user": {
                "username": self.user,
                "password": self.password,
            }
        }

        url = http.make_url(self.host, "/login", port=self.port, use_tls=self.use_tls)

        try:
            self.client.post(url, json=data)
        except Exception:
            logger.error(traceback.format_exc())


    def authenticate_oauth(self):
        """Performs authentication for OAuth client credentials
        """
        url = http.make_url(self.host, "/oauth/token", port=self.port, use_tls=self.use_tls)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            res = self.client.post(url, headers=headers, data=data)
            self.token = res.json()["access_token"]
        except Exception:
            logger.error(traceback.format_exc())

        self.token =  jsonutils.loads(res.body).get("access_token")



def platform_factory(
    host: str="localhost",
    port: int=0,
    use_tls: bool=True,
    verify: bool=True,
    user: str="admin",
    password: str="admin",
    client_id: str=None,
    client_secret: str=None,
    timeout: int=30
) -> Platform:
    """Create a new instance of a Platform connection.

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

    Returns:
        Platform: An initialized Platform connection instance.
    """
    return Platform(
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
