# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import httpx
import pytest

from ipsdk import exceptions
from ipsdk.connection import AsyncConnection
from ipsdk.connection import Connection
from ipsdk.connection import Response
from ipsdk.platform import AsyncAuthMixin
from ipsdk.platform import AsyncPlatformType
from ipsdk.platform import AuthMixin
from ipsdk.platform import Platform
from ipsdk.platform import PlatformType
from ipsdk.platform import _make_basicauth_body
from ipsdk.platform import _make_basicauth_path
from ipsdk.platform import _make_oauth_body
from ipsdk.platform import _make_oauth_headers
from ipsdk.platform import _make_oauth_path
from ipsdk.platform import platform_factory

# --------- Factory Tests ---------


def test_platform_factory_default():
    """Test platform_factory with default parameters."""
    conn = platform_factory()
    assert isinstance(conn, Platform)
    assert conn.user == "admin"
    assert conn.password == "admin"
    assert conn.client_id is None
    assert conn.client_secret is None


def test_platform_factory_returns_connection():
    """Test that platform_factory returns a Connection instance."""
    p = platform_factory()
    assert isinstance(p, Connection)


def test_platform_factory_returns_async():
    """Test that platform_factory returns AsyncConnection when want_async=True."""
    p = platform_factory(want_async=True)
    assert isinstance(p, AsyncConnection)


def test_platform_factory_custom_params():
    """Test platform_factory with custom parameters."""
    conn = platform_factory(
        host="platform.example.com",
        port=443,
        user="custom_user",
        password="custom_pass",
        client_id="test_client",
        client_secret="test_secret",
        use_tls=True,
        verify=False,
        timeout=120,
    )
    assert isinstance(conn, Platform)
    assert conn.user == "custom_user"
    assert conn.password == "custom_pass"
    assert conn.client_id == "test_client"
    assert conn.client_secret == "test_secret"


def test_platform_factory_oauth_only():
    """Test platform_factory with only OAuth credentials."""
    conn = platform_factory(
        client_id="oauth_client", client_secret="oauth_secret", user=None, password=None
    )
    assert conn.client_id == "oauth_client"
    assert conn.client_secret == "oauth_secret"
    assert conn.user is None
    assert conn.password is None


def test_platform_authentication_fallback():
    """Test platform authentication fails when no credentials provided."""
    conn = platform_factory(client_id=None, client_secret=None)
    # auth should fail gracefully since no server is running
    conn.client_id = None
    conn.client_secret = None
    conn.user = None
    conn.password = None
    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        conn.authenticate()


# --------- Helper Function Tests ---------


def test_make_oauth_headers():
    """Test _make_oauth_headers utility function."""
    headers = _make_oauth_headers()
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_make_oauth_path():
    """Test _make_oauth_path utility function."""
    assert _make_oauth_path() == "/oauth/token"


def test_make_oauth_body():
    """Test _make_oauth_body utility function."""
    result = _make_oauth_body("test_id", "test_secret")
    expected = {
        "grant_type": "client_credentials",
        "client_id": "test_id",
        "client_secret": "test_secret",
    }
    assert result == expected


def test_make_oauth_body_special_chars():
    """Test _make_oauth_body with special characters."""
    result = _make_oauth_body("client@domain.com", "secret!@#$%")
    expected = {
        "grant_type": "client_credentials",
        "client_id": "client@domain.com",
        "client_secret": "secret!@#$%",
    }
    assert result == expected


def test_make_basicauth_body():
    """Test _make_basicauth_body utility function."""
    result = _make_basicauth_body("testuser", "testpass")
    expected = {"user": {"username": "testuser", "password": "testpass"}}
    assert result == expected


def test_make_basicauth_path():
    """Test _make_basicauth_path utility function."""
    assert _make_basicauth_path() == "/login"


# --------- Sync AuthMixin Tests ---------


def test_authenticate_oauth_success():
    """Test AuthMixin.authenticate_oauth successful authentication."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "test_token_123"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch(
        "ipsdk.jsonutils.loads", return_value={"access_token": "test_token_123"}
    ):
        mixin.authenticate_oauth()

    assert mixin.token == "test_token_123"
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )


def test_authenticate_oauth_401_unauthorized():
    """Test AuthMixin.authenticate_oauth with 401 unauthorized."""
    mixin = AuthMixin()
    mixin.client_id = "invalid_id"
    mixin.client_secret = "invalid_secret"
    mixin.client = Mock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"


def test_authenticate_oauth_network_error():
    """Test AuthMixin.authenticate_oauth with network error."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock network error
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"
    exception = httpx.ConnectError("Connection refused", request=mock_request)
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate_oauth()

    assert "Network error during OAuth authentication" in str(exc_info.value)


def test_authenticate_user_success():
    """Test AuthMixin.authenticate_user successful authentication."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    mixin.authenticate_user()

    mixin.client.post.assert_called_once_with(
        "/login", json={"user": {"username": "testuser", "password": "testpass"}}
    )


def test_authenticate_user_401_unauthorized():
    """Test AuthMixin.authenticate_user with 401 unauthorized."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "wrongpass"
    mixin.client = Mock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_user()

    assert "Basic authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"


def test_authenticate_prefers_oauth():
    """Test that authenticate prefers OAuth when both credentials are available."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock OAuth success
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "oauth_token"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "oauth_token"}):
        mixin.authenticate()

    # Should have called OAuth, not basic auth
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )
    assert mixin.token == "oauth_token"


def test_authenticate_oauth_preferred_over_basic():
    """Test that authenticate uses OAuth when both OAuth and basic credentials are
    available."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock OAuth success
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "oauth_token"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "oauth_token"}):
        mixin.authenticate()

    # Should have called OAuth (not basic auth) since OAuth credentials are preferred
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )
    assert mixin.token == "oauth_token"


def test_authenticate_no_credentials_error():
    """Test authenticate raises error when no credentials provided."""
    mixin = AuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        mixin.authenticate()


# --------- Async AuthMixin Tests ---------


@pytest.mark.asyncio
async def test_async_authenticate_oauth_success():
    """Test AsyncAuthMixin.authenticate_oauth successful authentication."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "async_token_123"}'
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    with patch(
        "ipsdk.jsonutils.loads", return_value={"access_token": "async_token_123"}
    ):
        await mixin.authenticate_oauth()

    assert mixin.token == "async_token_123"
    mixin.client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_success():
    """Test AsyncAuthMixin.authenticate_basicauth successful authentication."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    await mixin.authenticate_basicauth()
    mixin.client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_authenticate_oauth_401_unauthorized():
    """Test AsyncAuthMixin.authenticate_oauth with 401 unauthorized."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "invalid_id"
    mixin.client_secret = "invalid_secret"
    mixin.client = AsyncMock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"


@pytest.mark.asyncio
async def test_async_authenticate_no_credentials_error():
    """Test async authenticate raises error when no credentials provided."""
    mixin = AsyncAuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        await mixin.authenticate()


# --------- Integration Tests ---------


def test_platform_integration_with_connection():
    """Test that Platform integrates properly with Connection base class."""
    platform = platform_factory()

    # Verify it has the expected connection methods
    assert hasattr(platform, "get")
    assert hasattr(platform, "post")
    assert hasattr(platform, "put")
    assert hasattr(platform, "delete")
    assert hasattr(platform, "patch")
    assert hasattr(platform, "authenticate")

    # Verify credentials are set correctly
    assert platform.user == "admin"
    assert platform.password == "admin"


def test_platform_base_url_construction():
    """Test that Platform constructs the correct base URL."""
    platform = platform_factory(host="platform.example.com", port=443, use_tls=True)

    # Platform should have no base path (direct to host)
    expected_base_url = "https://platform.example.com"
    assert str(platform.client.base_url) == expected_base_url


def test_platform_authentication_not_called_initially():
    """Test that Platform doesn't authenticate until first API call."""
    platform = platform_factory()

    # Authentication should not have been called yet
    assert not platform.authenticated
    assert platform.token is None


def test_platform_oauth_token_handling():
    """Test that Platform properly handles OAuth tokens."""
    platform = platform_factory(client_id="test_client", client_secret="test_secret")

    # Token should be None initially
    assert platform.token is None

    # After setting a token, it should be available
    platform.token = "test_token_value"
    assert platform.token == "test_token_value"


# --------- Missing OAuth Error Cases ---------


def test_authenticate_oauth_missing_access_token_dict():
    """Test OAuth authentication when response dict is missing access_token."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock response without access_token
    mock_response = Mock(spec=Response)
    mock_response.text = '{"token_type": "Bearer", "expires_in": 3600}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch(
        "ipsdk.jsonutils.loads",
        return_value={"token_type": "Bearer", "expires_in": 3600}
    ):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            mixin.authenticate_oauth()

        assert "OAuth response missing access_token field" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"
        assert "response_keys" in exc_info.value.details


def test_authenticate_oauth_non_dict_response():
    """Test OAuth authentication when response is not a dict."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock response that's not a dict
    mock_response = Mock(spec=Response)
    mock_response.text = '"invalid_response"'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value="invalid_response"):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            mixin.authenticate_oauth()

        assert "OAuth response is not a JSON object" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"
        assert "response_type" in exc_info.value.details


def test_authenticate_oauth_403_forbidden():
    """Test OAuth authentication with 403 forbidden."""
    mixin = AuthMixin()
    mixin.client_id = "forbidden_id"
    mixin.client_secret = "forbidden_secret"
    mixin.client = Mock()

    # Mock 403 response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Forbidden", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert exc_info.value.details.get("status_code") == 403


def test_authenticate_oauth_server_error():
    """Test OAuth authentication with server error (500)."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock 500 response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Server Error", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_oauth()

    assert "OAuth authentication failed with status 500" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert exc_info.value.details.get("status_code") == 500


def test_authenticate_oauth_validation_error():
    """Test OAuth authentication with JSON validation error."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock successful HTTP response
    mock_response = Mock(spec=Response)
    mock_response.text = "invalid json}"
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    # Mock ValidationError from jsonutils
    validation_error = exceptions.ValidationError("Invalid JSON")
    with patch("ipsdk.jsonutils.loads", side_effect=validation_error):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            mixin.authenticate_oauth()

        assert "Failed to parse OAuth response" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"
        assert "json_error" in exc_info.value.details


def test_authenticate_oauth_generic_exception():
    """Test OAuth authentication with generic exception."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock generic exception
    mixin.client.post.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_oauth()

    assert "Unexpected error during OAuth authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert "original_error" in exc_info.value.details


def test_authenticate_oauth_ipsdk_error_reraise():
    """Test that OAuth authentication re-raises IpsdkError instances."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock IpsdkError
    ipsdk_error = exceptions.NetworkError("Custom network error")
    mixin.client.post.side_effect = ipsdk_error

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate_oauth()

    assert "Custom network error" in str(exc_info.value)


# --------- Missing Basic Auth Error Cases ---------


def test_authenticate_user_403_forbidden():
    """Test basic authentication with 403 forbidden."""
    mixin = AuthMixin()
    mixin.user = "forbidden_user"
    mixin.password = "forbidden_pass"
    mixin.client = Mock()

    # Mock 403 response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Forbidden", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_user()

    assert "Basic authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details.get("status_code") == 403


def test_authenticate_user_server_error():
    """Test basic authentication with server error (500)."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock 500 response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Server Error", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_user()

    assert "Authentication failed with status 500" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details.get("status_code") == 500


def test_authenticate_user_generic_exception():
    """Test basic authentication with generic exception."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock generic exception
    mixin.client.post.side_effect = ValueError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_user()

    assert "Unexpected error during basic authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert "original_error" in exc_info.value.details


# --------- Missing Async Auth Cases ---------


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_403_forbidden():
    """Test async basic authentication with 403 forbidden."""
    mixin = AsyncAuthMixin()
    mixin.user = "forbidden_user"
    mixin.password = "forbidden_pass"
    mixin.client = AsyncMock()

    # Mock 403 response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Forbidden", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_basicauth()

    assert "Basic authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details.get("status_code") == 403


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_server_error():
    """Test async basic authentication with server error."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = AsyncMock()

    # Mock 500 response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Server Error", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_basicauth()

    assert "Authentication failed with status 500" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details.get("status_code") == 500


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_network_error():
    """Test async basic authentication with network error."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = AsyncMock()

    # Mock network error
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"
    exception = httpx.ConnectError("Connection refused", request=mock_request)
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.NetworkError) as exc_info:
        await mixin.authenticate_basicauth()

    assert "Network error during basic authentication" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_generic_exception():
    """Test async basic authentication with generic exception."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = AsyncMock()

    # Mock generic exception
    mixin.client.post.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_basicauth()

    assert "Unexpected error during basic authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert "original_error" in exc_info.value.details


@pytest.mark.asyncio
async def test_async_authenticate_oauth_missing_access_token():
    """Test async OAuth when response dict is missing access_token."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock response without access_token
    mock_response = Mock(spec=Response)
    mock_response.text = '{"token_type": "Bearer"}'
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"token_type": "Bearer"}):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            await mixin.authenticate_oauth()

        assert "OAuth response missing access_token field" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"


@pytest.mark.asyncio
async def test_async_authenticate_oauth_non_dict_response():
    """Test async OAuth when response is not a dict."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock response that's not a dict
    mock_response = Mock(spec=Response)
    mock_response.text = '["invalid", "response"]'
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value=["invalid", "response"]):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            await mixin.authenticate_oauth()

        assert "OAuth response is not a JSON object" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"
        assert "response_type" in exc_info.value.details


@pytest.mark.asyncio
async def test_async_authenticate_oauth_403_forbidden():
    """Test async OAuth authentication with 403 forbidden."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "forbidden_id"
    mixin.client_secret = "forbidden_secret"
    mixin.client = AsyncMock()

    # Mock 403 response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Forbidden", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert exc_info.value.details.get("status_code") == 403


@pytest.mark.asyncio
async def test_async_authenticate_oauth_server_error():
    """Test async OAuth authentication with server error."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock 500 response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Server Error", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "OAuth authentication failed with status 500" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert exc_info.value.details.get("status_code") == 500


@pytest.mark.asyncio
async def test_async_authenticate_oauth_validation_error():
    """Test async OAuth authentication with JSON validation error."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock successful HTTP response
    mock_response = Mock(spec=Response)
    mock_response.text = "invalid json}"
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    # Mock ValidationError from jsonutils
    validation_error = exceptions.ValidationError("Invalid JSON")
    with patch("ipsdk.jsonutils.loads", side_effect=validation_error):
        with pytest.raises(exceptions.AuthenticationError) as exc_info:
            await mixin.authenticate_oauth()

        assert "Failed to parse OAuth response" in str(exc_info.value)
        assert exc_info.value.details.get("auth_type") == "oauth"
        assert "json_error" in exc_info.value.details


@pytest.mark.asyncio
async def test_async_authenticate_oauth_generic_exception():
    """Test async OAuth authentication with generic exception."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock generic exception
    mixin.client.post.side_effect = ValueError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "Unexpected error during OAuth authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "oauth"
    assert "original_error" in exc_info.value.details


@pytest.mark.asyncio
async def test_async_authenticate_oauth_ipsdk_error_reraise():
    """Test that async OAuth authentication re-raises IpsdkError instances."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock IpsdkError
    ipsdk_error = exceptions.AuthenticationError("Custom auth error")
    mixin.client.post.side_effect = ipsdk_error

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "Custom auth error" in str(exc_info.value)


# --------- Platform Type and Factory Tests ---------


def test_platform_type_aliases():
    """Test that platform type aliases are correctly defined."""

    # Verify type aliases exist
    assert PlatformType is not None
    assert AsyncPlatformType is not None


def test_platform_factory_with_all_parameters():
    """Test platform_factory with all possible parameters."""
    conn = platform_factory(
        host="example.com",
        port=8443,
        use_tls=True,
        verify=False,
        user="admin",
        password="secret",
        client_id="oauth_client",
        client_secret="oauth_secret",
        timeout=120,
        want_async=False,
    )

    assert conn.user == "admin"
    assert conn.password == "secret"
    assert conn.client_id == "oauth_client"
    assert conn.client_secret == "oauth_secret"


def test_platform_factory_async_with_all_parameters():
    """Test platform_factory async version with all parameters."""
    conn = platform_factory(
        host="example.com",
        port=8443,
        use_tls=False,
        verify=True,
        user="testuser",
        password="testpass",
        client_id=None,
        client_secret=None,
        timeout=60,
        want_async=True,
    )

    assert isinstance(conn, AsyncConnection)
    assert conn.user == "testuser"
    assert conn.password == "testpass"


# --------- Missing Coverage Tests ---------


def test_authenticate_basic_auth_path():
    """Test authenticate() calls authenticate_user() with basic auth."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client_id = None  # No OAuth credentials
    mixin.client_secret = None
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    # Call authenticate - should choose basic auth path
    mixin.authenticate()

    # Verify basic auth was called
    mixin.client.post.assert_called_once_with(
        "/login", json={"user": {"username": "testuser", "password": "testpass"}}
    )


def test_authenticate_user_request_error():
    """Test basic authentication with httpx.RequestError (network error)."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock RequestError
    request_error = httpx.RequestError("Connection error")
    mixin.client.post.side_effect = request_error

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate_user()

    assert "Network error during basic authentication" in str(exc_info.value)
    assert exc_info.value.details["original_error"] == "Connection error"


@pytest.mark.asyncio
async def test_async_authenticate_basic_auth_path():
    """Test async authenticate() calls authenticate_basicauth() with basic auth."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client_id = None  # No OAuth credentials
    mixin.client_secret = None
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    # Call authenticate - should choose basic auth path
    await mixin.authenticate()

    # Verify basic auth was called
    mixin.client.post.assert_awaited_once()


def test_authenticate_oauth_request_error():
    """Test OAuth authentication with httpx.RequestError (network error)."""
    mixin = AuthMixin()
    mixin.client_id = "test_client"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock RequestError
    request_error = httpx.RequestError("Connection timeout")
    mixin.client.post.side_effect = request_error

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate_oauth()

    assert "Network error during OAuth authentication" in str(exc_info.value)
    assert exc_info.value.details["original_error"] == "Connection timeout"
