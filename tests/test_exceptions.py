# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import Mock, MagicMock
import httpx

from ipsdk import exceptions


class TestIpsdkError:
    """Test cases for the base IpsdkError exception class."""

    def test_basic_initialization(self):
        """Test basic exception initialization with just a message."""
        exc = exceptions.IpsdkError("Test error message")
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.details == {}

    def test_initialization_with_details(self):
        """Test exception initialization with details dictionary."""
        details = {"key1": "value1", "key2": 42}
        exc = exceptions.IpsdkError("Test error", details=details)
        assert str(exc) == "Test error. Details: {'key1': 'value1', 'key2': 42}"
        assert exc.message == "Test error"
        assert exc.details == details

    def test_initialization_with_none_details(self):
        """Test exception initialization with None details."""
        exc = exceptions.IpsdkError("Test error", details=None)
        assert str(exc) == "Test error"
        assert exc.details == {}

    def test_str_representation_with_details(self):
        """Test string representation includes details when present."""
        exc = exceptions.IpsdkError("Error", {"status": 500})
        assert "Details: {'status': 500}" in str(exc)

    def test_str_representation_without_details(self):
        """Test string representation without details."""
        exc = exceptions.IpsdkError("Simple error")
        assert str(exc) == "Simple error"
        assert "Details:" not in str(exc)


class TestConnectionError:
    """Test cases for ConnectionError and its subclasses."""

    def test_connection_error_basic(self):
        """Test basic ConnectionError initialization."""
        exc = exceptions.ConnectionError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.host is None
        assert exc.port is None

    def test_connection_error_with_host_port(self):
        """Test ConnectionError with host and port information."""
        exc = exceptions.ConnectionError("Failed to connect", host="example.com", port=443)
        assert exc.message == "Failed to connect"
        assert exc.host == "example.com"
        assert exc.port == 443
        assert exc.details["host"] == "example.com"
        assert exc.details["port"] == 443

    def test_network_error_inheritance(self):
        """Test that NetworkError inherits from ConnectionError."""
        exc = exceptions.NetworkError("Network issue")
        assert isinstance(exc, exceptions.ConnectionError)
        assert isinstance(exc, exceptions.IpsdkError)

    def test_timeout_error_with_timeout(self):
        """Test TimeoutError with timeout value."""
        exc = exceptions.TimeoutError("Request timed out", timeout=30.0)
        assert exc.message == "Request timed out"
        assert exc.timeout == 30.0
        assert exc.details["timeout"] == 30.0

    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits properly."""
        exc = exceptions.TimeoutError("Timeout")
        assert isinstance(exc, exceptions.NetworkError)
        assert isinstance(exc, exceptions.ConnectionError)
        assert isinstance(exc, exceptions.IpsdkError)


class TestAuthenticationError:
    """Test cases for AuthenticationError and its subclasses."""

    def test_authentication_error_basic(self):
        """Test basic AuthenticationError initialization."""
        exc = exceptions.AuthenticationError("Auth failed")
        assert exc.message == "Auth failed"
        assert exc.auth_type is None

    def test_authentication_error_with_type(self):
        """Test AuthenticationError with auth type."""
        exc = exceptions.AuthenticationError("OAuth failed", auth_type="oauth")
        assert exc.message == "OAuth failed"
        assert exc.auth_type == "oauth"
        assert exc.details["auth_type"] == "oauth"

    def test_token_error_inheritance(self):
        """Test that TokenError inherits from AuthenticationError."""
        exc = exceptions.TokenError("Invalid token")
        assert isinstance(exc, exceptions.AuthenticationError)
        assert isinstance(exc, exceptions.IpsdkError)

    def test_credentials_error_inheritance(self):
        """Test that CredentialsError inherits from AuthenticationError."""
        exc = exceptions.CredentialsError("Invalid credentials")
        assert isinstance(exc, exceptions.AuthenticationError)
        assert isinstance(exc, exceptions.IpsdkError)


class TestHTTPError:
    """Test cases for HTTPError and its subclasses."""

    def test_http_error_basic(self):
        """Test basic HTTPError initialization."""
        exc = exceptions.HTTPError("HTTP error")
        assert exc.message == "HTTP error"
        assert exc.status_code is None
        assert exc.response is None
        assert exc.request_url is None

    def test_http_error_with_all_params(self):
        """Test HTTPError with all parameters."""
        mock_response = Mock()
        mock_response.text = "Error response body"
        
        exc = exceptions.HTTPError(
            "HTTP 500 error",
            status_code=500,
            response=mock_response,
            request_url="https://example.com/api"
        )
        
        assert exc.message == "HTTP 500 error"
        assert exc.status_code == 500
        assert exc.response == mock_response
        assert exc.request_url == "https://example.com/api"
        assert exc.details["status_code"] == 500
        assert exc.details["request_url"] == "https://example.com/api"
        assert exc.details["response_body"] == "Error response body"

    def test_http_error_truncates_long_response(self):
        """Test that HTTPError truncates long response bodies."""
        mock_response = Mock()
        mock_response.text = "x" * 1000  # Long response body
        
        exc = exceptions.HTTPError("Error", response=mock_response)
        assert len(exc.details["response_body"]) == 500  # Should be truncated

    def test_client_error_inheritance(self):
        """Test that ClientError inherits from HTTPError."""
        exc = exceptions.ClientError("Client error", status_code=400)
        assert isinstance(exc, exceptions.HTTPError)
        assert isinstance(exc, exceptions.IpsdkError)
        assert exc.status_code == 400

    def test_server_error_inheritance(self):
        """Test that ServerError inherits from HTTPError."""
        exc = exceptions.ServerError("Server error", status_code=500)
        assert isinstance(exc, exceptions.HTTPError)
        assert isinstance(exc, exceptions.IpsdkError)
        assert exc.status_code == 500


class TestValidationError:
    """Test cases for ValidationError and its subclasses."""

    def test_validation_error_basic(self):
        """Test basic ValidationError initialization."""
        exc = exceptions.ValidationError("Validation failed")
        assert exc.message == "Validation failed"
        assert exc.field is None
        assert exc.value is None

    def test_validation_error_with_field_value(self):
        """Test ValidationError with field and value."""
        exc = exceptions.ValidationError("Invalid value", field="username", value="invalid@")
        assert exc.message == "Invalid value"
        assert exc.field == "username"
        assert exc.value == "invalid@"
        assert exc.details["field"] == "username"
        assert exc.details["value"] == "invalid@"

    def test_json_error_inheritance(self):
        """Test that JSONError inherits from ValidationError."""
        exc = exceptions.JSONError("JSON parse error")
        assert isinstance(exc, exceptions.ValidationError)
        assert isinstance(exc, exceptions.IpsdkError)


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_configuration_error_basic(self):
        """Test basic ConfigurationError initialization."""
        exc = exceptions.ConfigurationError("Config error")
        assert exc.message == "Config error"
        assert exc.config_key is None

    def test_configuration_error_with_key(self):
        """Test ConfigurationError with config key."""
        exc = exceptions.ConfigurationError("Missing config", config_key="api_key")
        assert exc.message == "Missing config"
        assert exc.config_key == "api_key"
        assert exc.details["config_key"] == "api_key"


class TestAPIError:
    """Test cases for APIError."""

    def test_api_error_basic(self):
        """Test basic APIError initialization."""
        exc = exceptions.APIError("API error")
        assert exc.message == "API error"
        assert exc.api_endpoint is None
        assert exc.api_version is None

    def test_api_error_with_endpoint_version(self):
        """Test APIError with endpoint and version."""
        exc = exceptions.APIError(
            "API deprecated", 
            api_endpoint="/v1/users",
            api_version="v1"
        )
        assert exc.message == "API deprecated"
        assert exc.api_endpoint == "/v1/users"
        assert exc.api_version == "v1"
        assert exc.details["api_endpoint"] == "/v1/users"
        assert exc.details["api_version"] == "v1"


class TestClassifyHTTPError:
    """Test cases for the classify_http_error function."""

    def test_classify_401_unauthorized(self):
        """Test classification of 401 Unauthorized."""
        exc = exceptions.classify_http_error(401, request_url="https://example.com")
        assert isinstance(exc, exceptions.HTTPError)
        assert exc.status_code == 401
        assert "Authentication failed" in exc.message
        assert exc.request_url == "https://example.com"

    def test_classify_403_forbidden(self):
        """Test classification of 403 Forbidden."""
        exc = exceptions.classify_http_error(403)
        assert isinstance(exc, exceptions.HTTPError)
        assert exc.status_code == 403
        assert "Access forbidden" in exc.message

    def test_classify_400_client_error(self):
        """Test classification of 4xx client errors."""
        exc = exceptions.classify_http_error(400)
        assert isinstance(exc, exceptions.ClientError)
        assert isinstance(exc, exceptions.HTTPError)
        assert exc.status_code == 400

    def test_classify_404_client_error(self):
        """Test classification of 404 Not Found."""
        exc = exceptions.classify_http_error(404)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 404

    def test_classify_500_server_error(self):
        """Test classification of 5xx server errors."""
        exc = exceptions.classify_http_error(500)
        assert isinstance(exc, exceptions.ServerError)
        assert isinstance(exc, exceptions.HTTPError)
        assert exc.status_code == 500

    def test_classify_503_server_error(self):
        """Test classification of 503 Service Unavailable."""
        exc = exceptions.classify_http_error(503)
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 503

    def test_classify_unknown_status_code(self):
        """Test classification of unknown status codes."""
        exc = exceptions.classify_http_error(999)
        assert isinstance(exc, exceptions.HTTPError)
        assert not isinstance(exc, exceptions.ClientError)
        assert not isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 999

    def test_classify_with_response_text(self):
        """Test classification with response text."""
        mock_response = Mock()
        mock_response.text = "Detailed error message"
        
        exc = exceptions.classify_http_error(400, response=mock_response)
        assert "Detailed error message" in exc.message
        assert isinstance(exc, exceptions.ClientError)

    def test_classify_with_long_response_text(self):
        """Test classification truncates long response text."""
        mock_response = Mock()
        mock_response.text = "x" * 300  # Long response
        
        exc = exceptions.classify_http_error(400, response=mock_response)
        assert len(exc.message) < 250  # Should be truncated

    def test_classify_with_response_parsing_error(self):
        """Test classification handles response parsing errors gracefully."""
        mock_response = Mock()
        # Make response.text property raise an exception when accessed
        type(mock_response).text = MagicMock(side_effect=Exception("Parse error"))
        
        exc = exceptions.classify_http_error(500, response=mock_response)
        assert isinstance(exc, exceptions.ServerError)
        assert "HTTP 500 error" in exc.message
        # Should not have response_body in details due to parse error
        assert "response_body" not in exc.details


class TestClassifyHttpxError:
    """Test cases for the classify_httpx_error function."""

    def test_classify_timeout_exception(self):
        """Test classification of httpx.TimeoutException."""
        httpx_exc = httpx.TimeoutException("Request timeout")
        exc = exceptions.classify_httpx_error(httpx_exc, "https://example.com")
        
        assert isinstance(exc, exceptions.TimeoutError)
        assert "Request timed out" in exc.message
        assert exc.details["request_url"] == "https://example.com"
        assert exc.details["original_error"] == "Request timeout"

    def test_classify_connect_error(self):
        """Test classification of httpx.ConnectError."""
        httpx_exc = httpx.ConnectError("Connection refused")
        exc = exceptions.classify_httpx_error(httpx_exc, "https://example.com")
        
        assert isinstance(exc, exceptions.NetworkError)
        assert "Failed to connect" in exc.message
        assert exc.details["request_url"] == "https://example.com"

    def test_classify_http_status_error(self):
        """Test classification of httpx.HTTPStatusError."""
        mock_request = Mock()
        mock_request.url = "https://example.com/api"
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        
        httpx_exc = httpx.HTTPStatusError("404 Not Found", request=mock_request, response=mock_response)
        exc = exceptions.classify_httpx_error(httpx_exc)
        
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 404

    def test_classify_request_error(self):
        """Test classification of generic httpx.RequestError."""
        httpx_exc = httpx.RequestError("Generic request error")
        exc = exceptions.classify_httpx_error(httpx_exc)
        
        assert isinstance(exc, exceptions.NetworkError)
        assert "Request error" in exc.message
        assert exc.details["original_error"] == "Generic request error"

    def test_classify_unknown_exception(self):
        """Test classification of unknown exceptions."""
        unknown_exc = ValueError("Unknown error")
        exc = exceptions.classify_httpx_error(unknown_exc, "https://example.com")
        
        assert isinstance(exc, exceptions.IpsdkError)
        assert "Unexpected error" in exc.message
        assert exc.details["request_url"] == "https://example.com"
        assert exc.details["original_error"] == "Unknown error"

    def test_classify_http_status_error_without_request(self):
        """Test classification of HTTPStatusError without request object."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        # Create a mock HTTPStatusError that behaves like the real one
        mock_httpx_exc = Mock(spec=httpx.HTTPStatusError)
        mock_httpx_exc.response = mock_response
        # Simulate request property access raising RuntimeError
        type(mock_httpx_exc).request = MagicMock(side_effect=RuntimeError("The .request property has not been set."))
        
        exc = exceptions.classify_httpx_error(mock_httpx_exc, "https://fallback.com")
        
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 500


class TestExceptionHierarchy:
    """Test cases to verify the exception hierarchy is correct."""

    def test_all_exceptions_inherit_from_ipsdk_error(self):
        """Test that all custom exceptions inherit from IpsdkError."""
        exception_classes = [
            exceptions.ConnectionError,
            exceptions.NetworkError,
            exceptions.TimeoutError,
            exceptions.AuthenticationError,
            exceptions.TokenError,
            exceptions.CredentialsError,
            exceptions.HTTPError,
            exceptions.ClientError,
            exceptions.ServerError,
            exceptions.ValidationError,
            exceptions.JSONError,
            exceptions.ConfigurationError,
            exceptions.APIError,
        ]
        
        for exc_class in exception_classes:
            exc = exc_class("Test message")
            assert isinstance(exc, exceptions.IpsdkError)

    def test_exception_inheritance_chain(self):
        """Test specific inheritance chains."""
        # NetworkError -> ConnectionError -> IpsdkError
        network_exc = exceptions.NetworkError("Network error")
        assert isinstance(network_exc, exceptions.ConnectionError)
        assert isinstance(network_exc, exceptions.IpsdkError)
        
        # TimeoutError -> NetworkError -> ConnectionError -> IpsdkError
        timeout_exc = exceptions.TimeoutError("Timeout")
        assert isinstance(timeout_exc, exceptions.NetworkError)
        assert isinstance(timeout_exc, exceptions.ConnectionError)
        assert isinstance(timeout_exc, exceptions.IpsdkError)
        
        # ClientError -> HTTPError -> IpsdkError
        client_exc = exceptions.ClientError("Client error")
        assert isinstance(client_exc, exceptions.HTTPError)
        assert isinstance(client_exc, exceptions.IpsdkError)

    def test_can_catch_by_base_class(self):
        """Test that exceptions can be caught by their base classes."""
        try:
            raise exceptions.TokenError("Invalid token")
        except exceptions.AuthenticationError as e:
            assert isinstance(e, exceptions.TokenError)
        except Exception:
            pytest.fail("Should have been caught as AuthenticationError")
        
        try:
            raise exceptions.ClientError("Bad request")
        except exceptions.HTTPError as e:
            assert isinstance(e, exceptions.ClientError)
        except Exception:
            pytest.fail("Should have been caught as HTTPError")

    def test_can_catch_all_by_ipsdk_error(self):
        """Test that all SDK exceptions can be caught by IpsdkError."""
        exceptions_to_test = [
            exceptions.NetworkError("Network"),
            exceptions.TokenError("Token"),
            exceptions.ClientError("Client"),
            exceptions.JSONError("JSON"),
            exceptions.ConfigurationError("Config"),
        ]
        
        for exc in exceptions_to_test:
            try:
                raise exc
            except exceptions.IpsdkError:
                pass  # Expected
            except Exception:
                pytest.fail(f"{type(exc)} should be catchable as IpsdkError")


class TestExceptionUsagePatterns:
    """Test common usage patterns for the exceptions."""

    def test_exception_chaining(self):
        """Test that exceptions can be properly chained."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise exceptions.ValidationError("Validation failed") from e
        except exceptions.ValidationError as exc:
            assert exc.__cause__ is not None
            assert str(exc.__cause__) == "Original error"

    def test_exception_details_mutation(self):
        """Test that exception details can be modified after creation."""
        exc = exceptions.HTTPError("HTTP error")
        exc.details["custom_field"] = "custom_value"
        assert exc.details["custom_field"] == "custom_value"

    def test_exception_repr(self):
        """Test exception __repr__ method works correctly."""
        exc = exceptions.ValidationError("Test error", field="test_field")
        repr_str = repr(exc)
        assert "ValidationError" in repr_str
        assert "Test error" in repr_str

    def test_exception_equality(self):
        """Test that exceptions with same message are not equal (object identity)."""
        exc1 = exceptions.IpsdkError("Same message")
        exc2 = exceptions.IpsdkError("Same message")
        assert exc1 is not exc2
        assert exc1 != exc2  # Different instances should not be equal