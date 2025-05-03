# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from unittest.mock import Mock, patch, AsyncMock

from ipsdk.connection import Connection, AsyncConnection

from ipsdk.platform import (
    _make_oauth_headers,
    _make_oauth_path,
    _make_oauth_body,
    _make_basicauth_body,
    _make_basicauth_path,
    AuthMixin,
    AsyncAuthMixin,
    platform_factory,
    Platform
)



def test_platform_factory_default():
    conn = platform_factory()
    assert isinstance(conn, Platform)
    assert conn.user == "admin"
    assert conn.password == "admin"
    assert conn.client_id is None
    assert conn.client_secret is None


def test_platform_factory_returns_connection():
    p = platform_factory()
    assert isinstance(p, Connection)


def test_platform_factory_returns_async():
    p = platform_factory(want_async=True)
    assert isinstance(p, AsyncConnection)



def test_platform_authentication_fallback():
    conn = platform_factory(client_id=None, client_secret=None)
    # auth should fail gracefully since no server is running
    with pytest.raises(ValueError, match="no authentication methods left to try"):
        conn.client_id = None
        conn.client_secret = None
        conn.user = None
        conn.password = None
        conn.authenticate()


# ---- Helper Function Tests ----

def test_make_oauth_headers():
    assert _make_oauth_headers() == {"Content-Type": "application/x-www-form-urlencoded"}


def test_make_oauth_path():
    assert _make_oauth_path() == "/oauth/token"


def test_make_oauth_body():
    assert _make_oauth_body("id", "secret") == {
        "grant_type": "client_credentials",
        "client_id": "id",
        "client_secret": "secret"
    }


def test_make_basicauth_body():
    assert _make_basicauth_body("user", "pass") == {
        "user": {"username": "user", "password": "pass"}
    }


def test_make_basicauth_path():
    assert _make_basicauth_path() == "/login"


# ---- AuthMixin Tests ----

def test_authenticate_oauth_sets_token():
    mixin = AuthMixin()
    mixin.client_id = "id"
    mixin.client_secret = "secret"
    mixin.client = Mock()

    mock_response = Mock()
    mock_response.text = '{"access_token": "abc"}'
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "abc"}):
        mixin.authenticate_oauth()

    assert mixin.token == "abc"


def test_authenticate_user_calls_post():
    mixin = AuthMixin()
    mixin.user = "u"
    mixin.password = "p"
    mixin.client = Mock()

    mock_response = Mock()
    mixin.client.post.return_value = mock_response

    mixin.authenticate_user()
    mixin.client.post.assert_called_once()


def test_authenticate_value_error():
    mixin = AuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(ValueError):
        mixin.authenticate()


# ---- AsyncAuthMixin Tests ----

@pytest.mark.asyncio
async def test_async_oauth_sets_token():
    mixin = AsyncAuthMixin()
    mixin.client_id = "id"
    mixin.client_secret = "secret"
    mixin.client = AsyncMock()

    mock_response = AsyncMock()
    mock_response.text = '{"access_token": "abc"}'
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "abc"}):
        await mixin.authenticate_oauth()

    assert mixin.token == "abc"


@pytest.mark.asyncio
async def test_async_user_calls_post():
    mixin = AsyncAuthMixin()
    mixin.user = "u"
    mixin.password = "p"
    mixin.client = AsyncMock()

    mock_response = AsyncMock()
    mixin.client.post.return_value = mock_response

    await mixin.authenticate_basicauth()
    mixin.client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_authenticate_value_error():
    mixin = AsyncAuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(ValueError):
        await mixin.authenticate()

