# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import traceback

from . import http
from . import logger


class Gateway(http.Connection):
    """ Gateway is a HTTP connection to an Itential Automation Gateway
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
        data = {
            "username": self.user,
            "password": self.password,
        }

        url = http.make_url(
            self.host, "/login", base_path=self.base_path, port=self.port, use_tls=self.use_tls
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            self.client.post(url, headers=headers, json=data)
        except Exception:
            logger.error(traceback.format_exc())


def gateway_factory(
    host: str="localhost",
    port: int=0,
    use_tls: bool=True,
    verify: bool=True,
    user: str="admin@itential",
    password: str="admin",
    timeout: int=30
) -> Gateway:
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

    Returns:
        Gateway: An initialized Gateway connection instance with a base API path set.
    """
    return Gateway(
        host=host,
        port=port,
        use_tls=use_tls,
        verify=verify,
        user=user,
        password=password,
        timeout=timeout,
        base_path="/api/v2.0",
    )
