# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import Mock, AsyncMock

import pytest


# Replace 'ipsdk' with the actual filename (without .py)
from ipsdk.gateway import (
    _make_path,
    _make_body,
    _make_headers,
    AuthMixin,
    AsyncAuthMixin,
    gateway_factory,
    Gateway
)

def test_gateway_factory_default():
    conn = gateway_factory()
    assert isinstance(conn, Gateway)
    assert conn.user == "admin@itential"
    assert conn.password == "admin"

# --------- Utility Function Tests ---------

def test_make_path():
    assert _make_path() == "/login"


def test_make_body():
    assert _make_body("user1", "pass1") == {
        "username": "user1",
        "password": "pass1"
    }


def test_make_headers():
    headers = _make_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


# --------- Sync AuthMixin Tests ---------

def test_auth_mixin_authenticate_calls_post():
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    mixin.authenticate()

    mixin.client.post.assert_called_once_with(
        "/login",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={"username": "admin", "password": "adminpass"}
    )

# --------- Async AsyncAuthMixin Tests ---------

@pytest.mark.asyncio
async def test_async_auth_mixin_authenticate_calls_post():
    mixin = AsyncAuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = AsyncMock()

    await mixin.authenticate()

    mixin.client.post.assert_awaited_once_with(
        "/login",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={"username": "admin", "password": "adminpass"}
    )
