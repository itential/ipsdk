# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ipsdk.platform import platform_factory, Platform


def test_platform_factory_default():
    conn = platform_factory()
    assert isinstance(conn, Platform)
    assert conn.host == "localhost"
    assert conn.user == "admin"
    assert conn.password == "admin"


def test_platform_repr():
    conn = platform_factory()
    assert repr(conn) == "Platform(host='localhost')"


def test_platform_str():
    conn = platform_factory()
    assert str(conn) == repr(conn)


def test_platform_authentication_fallback():
    conn = platform_factory(client_id=None, client_secret=None)
    # auth should fail gracefully since no server is running
    with pytest.raises(ValueError, match="no authentication methods left to try"):
        conn.client_id = None
        conn.client_secret = None
        conn.user = None
        conn.password = None
        conn.authenticate()
