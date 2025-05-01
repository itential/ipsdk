# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk.gateway import gateway_factory, Gateway


def test_gateway_factory_default():
    conn = gateway_factory()
    assert isinstance(conn, Gateway)
    assert conn.host == "localhost"
    assert conn.user == "admin@itential"
    assert conn.password == "admin"


def test_gateway_repr():
    conn = gateway_factory()
    assert repr(conn) == "Gateway(host='localhost')"


def test_gateway_str():
    conn = gateway_factory()
    assert str(conn) == repr(conn)
