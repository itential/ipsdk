# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Custom exception hierarchy for the Itential Python SDK.

This module provides a comprehensive set of exceptions that provide specific
error information for different types of failures that can occur when using
the SDK.
"""

from typing import Optional, Dict, Any
import httpx


class IpsdkError(Exception):
    """
    Base exception class for all Itential SDK errors.
    
    All SDK-specific exceptions inherit from this base class, making it easy
    to catch any SDK-related error.
    
    Args:
        message (str): Human-readable error message
        details (dict): Additional error details and context
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the base SDK exception.
        
        Args:
            message (str): Human-readable error message
            details (dict): Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """
        Return a string representation of the error.
        
        Returns:
            A formatted error message including details if available
        """
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class ConnectionError(IpsdkError):
    """
    Exception raised for connection-related errors.
    
    This exception is raised when there are issues establishing or maintaining
    a connection to the Itential Platform or Gateway.
    
    Args:
        message (str): Human-readable error message
        host (str): The host that failed to connect
        port (int): The port that failed to connect
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, host: Optional[str] = None, 
                 port: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the connection error.
        
        Args:
            message (str): Human-readable error message
            host (str): Optional hostname that failed
            port (int): Optional port that failed
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.host = host
        self.port = port
        if host:
            self.details.update({"host": host})
        if port:
            self.details.update({"port": port})


class NetworkError(ConnectionError):
    """
    Exception raised for network-level communication errors.
    
    This includes DNS resolution failures, connection timeouts, and other
    low-level network issues.
    """
    pass


class TimeoutError(NetworkError):
    """
    Exception raised when a request times out.
    
    Args:
        message (str): Human-readable error message
        timeout (float): The timeout value that was exceeded
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, timeout: Optional[float] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the timeout error.
        
        Args:
            message (str): Human-readable error message
            timeout (float): Optional timeout value that was exceeded
            details (dict): Optional additional error context
        """
        super().__init__(message, details=details)
        self.timeout = timeout
        if timeout:
            self.details.update({"timeout": timeout})


class AuthenticationError(IpsdkError):
    """
    Exception raised for authentication-related errors.
    
    This includes failed login attempts, invalid credentials, and token-related
    issues.
    
    Args:
        message (str): Human-readable error message
        auth_type (str): The type of authentication that failed
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, auth_type: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the authentication error.
        
        Args:
            message (str): Human-readable error message
            auth_type (str): Optional authentication type (oauth, basic)
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.auth_type = auth_type
        if auth_type:
            self.details.update({"auth_type": auth_type})


class TokenError(AuthenticationError):
    """
    Exception raised for token-specific authentication errors.
    
    This includes expired tokens, invalid tokens, and token refresh failures.
    """
    pass


class CredentialsError(AuthenticationError):
    """
    Exception raised for credential-related errors.
    
    This includes missing credentials, invalid usernames/passwords, and
    malformed client credentials.
    """
    pass


class HTTPError(IpsdkError):
    """
    Exception raised for HTTP-related errors.
    
    This includes HTTP status errors, malformed responses, and protocol-level
    issues.
    
    Args:
        message (str): Human-readable error message
        status_code (int): HTTP status code if available
        response (httpx.Response): The HTTP response object if available
        request_url (str): The URL that was requested
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None,
                 response: Optional[httpx.Response] = None,
                 request_url: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the HTTP error.
        
        Args:
            message (str): Human-readable error message
            status_code (int): Optional HTTP status code
            response (httpx.Response): Optional HTTP response object
            request_url (str): Optional URL that was requested
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response = response
        self.request_url = request_url
        
        if status_code:
            self.details.update({"status_code": status_code})
        if request_url:
            self.details.update({"request_url": request_url})
        if response and hasattr(response, 'text'):
            try:
                response_text = response.text
                if isinstance(response_text, str):
                    self.details.update({"response_body": response_text[:500]})  # Limit response body size
            except Exception:
                # Ignore errors when accessing response text
                pass


class ClientError(HTTPError):
    """
    Exception raised for HTTP 4xx client errors.
    
    This includes bad requests, unauthorized access, forbidden resources, and
    not found errors.
    """
    pass


class ServerError(HTTPError):
    """
    Exception raised for HTTP 5xx server errors.
    
    This includes internal server errors, bad gateways, and service unavailable
    errors.
    """
    pass


class ValidationError(IpsdkError):
    """
    Exception raised for data validation errors.
    
    This includes invalid input parameters, malformed JSON, and schema
    validation failures.
    
    Args:
        message (str): Human-readable error message
        field (str): The field that failed validation
        value (Any): The value that failed validation
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the validation error.
        
        Args:
            message (str): Human-readable error message
            field (str): Optional field name that failed validation
            value (Any): Optional value that failed validation
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.field = field
        self.value = value
        
        if field:
            self.details.update({"field": field})
        if value is not None:
            self.details.update({"value": str(value)})


class JSONError(ValidationError):
    """
    Exception raised for JSON parsing and serialization errors.
    
    This includes malformed JSON data, encoding issues, and JSON schema
    validation failures.
    """
    pass


class ConfigurationError(IpsdkError):
    """
    Exception raised for configuration-related errors.
    
    This includes missing required configuration, invalid configuration values,
    and configuration file errors.
    
    Args:
        message (str): Human-readable error message
        config_key (str): The configuration key that caused the error
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration error.
        
        Args:
            message (str): Human-readable error message
            config_key (str): Optional configuration key that caused the error
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.config_key = config_key
        
        if config_key:
            self.details.update({"config_key": config_key})


class APIError(IpsdkError):
    """
    Exception raised for API-specific errors.
    
    This includes API version mismatches, unsupported operations, and
    API-specific error responses.
    
    Args:
        message (str): Human-readable error message
        api_endpoint (str): The API endpoint that caused the error
        api_version (str): The API version being used
        details (dict): Additional error details
    """
    
    def __init__(self, message: str, api_endpoint: Optional[str] = None,
                 api_version: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the API error.
        
        Args:
            message (str): Human-readable error message
            api_endpoint (str): Optional API endpoint that caused the error
            api_version (str): Optional API version
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.api_endpoint = api_endpoint
        self.api_version = api_version
        
        if api_endpoint:
            self.details.update({"api_endpoint": api_endpoint})
        if api_version:
            self.details.update({"api_version": api_version})


def classify_http_error(status_code: int, response: Optional[httpx.Response] = None,
                       request_url: Optional[str] = None) -> "HTTPError":
    """
    Classify HTTP status codes into appropriate exception types.
    
    Args:
        status_code (int): HTTP status code
        response (httpx.Response): Optional HTTP response object
        request_url (str): Optional URL that was requested
    
    Returns:
        An appropriate HTTPError subclass instance
    
    Raises:
        HTTPError: For status codes that don't fit specific categories
    """
    message = f"HTTP {status_code} error"
    
    if response and hasattr(response, 'text'):
        try:
            # Try to get more specific error message from response
            response_text = response.text[:200]  # Limit message length
            if response_text:
                message = f"HTTP {status_code} error: {response_text}"
        except Exception:
            pass  # Use default message if response parsing fails
    
    if 400 <= status_code < 500:
        if status_code == 401:
            return HTTPError(
                message="Authentication failed - invalid credentials or expired token",
                status_code=status_code,
                response=response,
                request_url=request_url
            )
        elif status_code == 403:
            return HTTPError(
                message="Access forbidden - insufficient permissions",
                status_code=status_code,
                response=response,
                request_url=request_url
            )
        else:
            return ClientError(message, status_code, response, request_url)
    
    elif 500 <= status_code < 600:
        return ServerError(message, status_code, response, request_url)
    
    else:
        return HTTPError(message, status_code, response, request_url)


def classify_httpx_error(exc: Exception, request_url: Optional[str] = None) -> IpsdkError:
    """
    Classify httpx exceptions into appropriate SDK exception types.
    
    Args:
        exc (Exception): The httpx exception to classify
        request_url (str): Optional URL that was requested
    
    Returns:
        An appropriate IpsdkError subclass instance
    """
    if isinstance(exc, httpx.TimeoutException):
        return TimeoutError(
            message=f"Request timed out: {str(exc)}",
            details={"request_url": request_url, "original_error": str(exc)}
        )
    
    elif isinstance(exc, httpx.ConnectError):
        return NetworkError(
            message=f"Failed to connect: {str(exc)}",
            details={"request_url": request_url, "original_error": str(exc)}
        )
    
    elif isinstance(exc, httpx.HTTPStatusError):
        try:
            url = str(exc.request.url) if exc.request else request_url
        except (RuntimeError, AttributeError):
            url = request_url
        return classify_http_error(
            exc.response.status_code,
            exc.response,
            url
        )
    
    elif isinstance(exc, httpx.RequestError):
        return NetworkError(
            message=f"Request error: {str(exc)}",
            details={"request_url": request_url, "original_error": str(exc)}
        )
    
    else:
        return IpsdkError(
            message=f"Unexpected error: {str(exc)}",
            details={"request_url": request_url, "original_error": str(exc)}
        )