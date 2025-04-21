# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import logging

from functools import partial

from . import http
from . import stringutils

logger = logging.getLogger(__name__)


class Gateway(http.Connection):
    """
    Gateway is a HTTP connection to an Itential Automation Gateway
    """

    def authenticate(self):
        """Provides the authentication function for authenticating to the server
        """
        data = {
            "username": self.user,
            "password": self.password,
        }

        url = http.make_url(self.host, "/login", base_path=self.base_path, port=self.port, use_tls=self.use_tls)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        res = self.session.post(url, headers=headers, json=data)
        res.raise_for_status()


class Cloud(http.Connection):
    """
    Cloud is a HTTP connection to Itential Automation Service
    """

    def authenticate(self):
        """Provides the authentication function for authenticating to the server
        """
        url = http.make_url(self.host, "/token", port=self.port, use_tls=self.use_tls)

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        res = self.session.post(url, headers=headers, json=data)
        res.raise_for_status()

        self.token = res.json()["access_token"]
        self.authenticated = True



class Platform(http.Connection):
    """
    Platform is a HTTP connection to Itential Platform
    """

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
        res = self.session.post(url, json=data)
        res.raise_for_status()

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

        res = self.session.post(url, headers=headers, data=data)
        res.raise_for_status()

        self.token = res.json()["access_token"]


def get(f, key, value, default):
    if value is None:
        value = os.getenv(f"ITENTIAL_{key}".upper(), default)
    return f(value)


getstr = partial(get, stringutils.tostr)
getint = partial(get, stringutils.toint)
getbool = partial(get, stringutils.tobool)


def cloud(host=None, port=0, use_tls=True, verify=True, client_id=None, client_secret=None, timeout=30):
    """
    Create a new instance of a Cloud connection.

    This factory function initializes a Cloud connection using either provided arguments
    or environment variable overrides. It supports authentication using client credentials.

    Environment Variables (override arguments if set):
        - ITENTIAL_HOST
        - ITENTIAL_PORT
        - ITENTIAL_USE_TLS
        - ITENTIAL_VERIFY
        - ITENTIAL_CLIENT_ID
        - ITENTIAL_CLIENT_SECRET
        - ITENTIAL_TIMEOUT

    Args:
        host (str): The target host for the connection.
        port (int): Port number to connect to.
        use_tls (bool): Whether to use TLS for the connection.
        verify (bool): Whether to verify SSL certificates.
        client_id (str): Client ID for authentication.
        client_secret (str): Client secret for authentication.
        timeout (int): Timeout for the connection, in seconds.

    Returns:
        Cloud: An initialized Cloud connection instance.
    """
    return Cloud(
        host=getstr("host", host, None),
        port=getint("port", port, 0),
        use_tls=getbool("use_tls", use_tls, True),
        verify=getbool("verify", verify, True),
        client_id=getstr("client_id", client_id, None),
        client_secret=getstr("client_secret", client_secret, None),
        timeout=getint("timeout", timeout, 30),
    )

def platform(host=None, port=0, use_tls=True, verify=True, user="admin", password="admin", client_id=None, client_secret=None, timeout=30):
    """
    Create a new instance of a Platform connection.

    This factory function initializes a Platform connection using provided parameters or
    environment variable overrides. Supports both user/password and client credentials.

    Environment Variables (override arguments if set):
        - ITENTIAL_HOST
        - ITENTIAL_PORT
        - ITENTIAL_USE_TLS
        - ITENTIAL_VERIFY
        - ITENTIAL_USER
        - ITENTIAL_PASSWORD
        - ITENTIAL_CLIENT_ID
        - ITENTIAL_CLIENT_SECRET
        - ITENTIAL_TIMEOUT

    Args:
        host (str): The target host for the connection.
        port (int): Port number to connect to.
        use_tls (bool): Whether to use TLS for the connection.
        verify (bool): Whether to verify SSL certificates.
        user (str): Username for authentication.
        password (str): Password for authentication.
        client_id (str): Optional client ID for token-based auth.
        client_secret (str): Optional client secret for token-based auth.
        timeout (int): Timeout for the connection, in seconds.

    Returns:
        Platform: An initialized Platform connection instance.
    """
    return Platform(
        host=getstr("host", host, None),
        port=getint("port", port, 0),
        use_tls=getbool("use_tls", use_tls, True),
        verify=getbool("verify", verify, True),
        user=getstr("user", user, "admin"),
        password=getstr("password", password, "admin"),
        client_id=getstr("client_id", client_id, None),
        client_secret=getstr("client_secret", client_secret, None),
        timeout=getint("timeout", timeout, 30),
    )


def gateway(host=None, port=0, use_tls=True, verify=True, user="admin@itential", password="admin", timeout=30):
    """
    Create a new instance of a Gateway connection.

    This factory function initializes a Gateway connection using provided parameters or
    environment variable overrides. Uses basic username/password authentication.

    Environment Variables (override arguments if set):
        - ITENTIAL_HOST
        - ITENTIAL_PORT
        - ITENTIAL_USE_TLS
        - ITENTIAL_VERIFY
        - ITENTIAL_USER
        - ITENTIAL_PASSWORD
        - ITENTIAL_TIMEOUT

    Args:
        host (str): The target host for the connection.
        port (int): Port number to connect to.
        use_tls (bool): Whether to use TLS for the connection.
        verify (bool): Whether to verify SSL certificates.
        user (str): Username for authentication.
        password (str): Password for authentication.
        timeout (int): Timeout for the connection, in seconds.

    Returns:
        Gateway: An initialized Gateway connection instance with a base API path set.
    """
    return Gateway(
        host=getstr("host", host, None),
        port=getint("port", port, 0),
        use_tls=getbool("use_tls", use_tls, True),
        verify=getbool("verify", verify, True),
        user=getstr("user", user, "admin"),
        password=getstr("password", password, "admin"),
        timeout=getint("timeout", timeout, 30),
        base_path="/api/v2.0",
    )
