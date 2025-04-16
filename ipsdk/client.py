# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import logging

from . import http
from . import stringutils

logger = logging.getLogger(__name__)


class Gateway(http.Connection):

    def authenticate(self):
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

    def authenticate(self):
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

    def authenticate(self):
        if self.client_id is not None and self.client_secret is not None:
            self.authenticate_oauth()
        elif self.user is not None and self.password is not None:
            self.authenticate_user()
        else:
            raise ValueError("no authentication methods left to try")
        self.authenticated = True

    def authenticate_user(self):
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


def cloud(host=None, port=0, use_tls=True, verify=True, client_id=None, client_secret=None, timeout=30):
    return Cloud(
        host=os.getenv("ITENTIAL_HOST", host),
        port=stringutils.string_to_int(os.getenv("ITENTIAL_PORT", port)),
        use_tls=stringutils.string_to_bool(os.getenv("ITENTIAL_USE_TLS", use_tls)),
        verify=stringutils.string_to_bool(os.getenv("ITENTIAL_VERIFY", verify)),
        client_id=os.getenv("ITENTIAL_CLIENT_ID", client_id),
        client_secret=os.getenv("ITENTIAL_CLIENT_SECRET", client_secret),
        timeout=stringutils.string_to_int(os.getenv("ITENTIAL_TIMEOUT", timeout)),
    )


def platform(host=None, port=0, use_tls=True, verify=True, user="admin", password="admin", client_id=None, client_secret=None, timeout=30):
    return Platform(
        host=os.getenv("ITENTIAL_HOST", host),
        port=stringutils.string_to_int(os.getenv("ITENTIAL_PORT", port)),
        use_tls=stringutils.string_to_bool(os.getenv("ITENTIAL_USE_TLS", use_tls)),
        verify=stringutils.string_to_bool(os.getenv("ITENTIAL_VERIFY", verify)),
        user=os.getenv("ITENTIAL_USER", user),
        password=os.getenv("ITENTIAL_PASSWORD", password),
        client_id=os.getenv("ITENTIAL_CLIENT_ID", client_id),
        client_secret=os.getenv("ITENTIAL_CLIENT_SECRET", client_secret),
        timeout=stringutils.string_to_int(os.getenv("ITENTIAL_TIMEOUT", timeout))
    )


def gateway(host=None, port=0, use_tls=True, verify=True, user="admin@itential", password="admin", timeout=30):
    return Gateway(
        host=os.getenv("ITENTIAL_HOST", host),
        port=stringutils.string_to_int(os.getenv("ITENTIAL_PORT", port)),
        use_tls=stringutils.string_to_bool(os.getenv("ITENTIAL_USE_TLS", use_tls)),
        verify=stringutils.string_to_bool(os.getenv("ITENTIAL_VERIFY", verify)),
        user=os.getenv("ITENTIAL_USER", user),
        password=os.getenv("ITENTIAL_PASSWORD", password),
        timeout=stringutils.string_to_int(os.getenv("ITENTIAL_TIMEOUT", timeout)),
        base_path="/api/v2.0"
    )
