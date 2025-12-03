# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import abc
import traceback
import urllib.parse
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import httpx

from . import exceptions
from . import logging
from . import metadata
from .http import HTTPMethod
from .http import HTTPStatus
from .http import Response


class ConnectionBase:

    client: Union[httpx.Client, httpx.AsyncClient]

    def __init__(
        self,
        host: str,
        port: int = 0,
        base_path: Optional[str] = None,
        use_tls: bool = True,
        verify: bool = True,
        user: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """
        Base class for all connection classes

        ConnectionBase is the base connection type that all connection classes
        are derived from.  It provides a set of common properties used by both
        the sync and async connection types.

        Args:
            host (str): The hostname or IP address to connect to

            port (int): The port value used when connecting to the API.  If
                this value is 0, the actual port value will be auto determined
                using the value of use_tls.  When use_tls is True, the port
                value will be set to 443 and when use_tls is False, the port
                value will be set to 80.  The default value for port is 0.

            base_path (str): The base url that is prepended to requests.  This
                value should not include the hostname or port value.  The
                default value is None

            use_tls (bool): Enable or disable TLS for this connection.  When
                this value is set to True, TLS will be enabled on the
                connection and when this value is set to False, TLS will be
                disabled.  The default value is True

            verify (bool): Enable or disable certificate verification.  When
                this value is set to True, certificates from the server are
                verified and when this value is set to False, certificate
                verification is disabled.  The default value for is True

            user (str): The username used to authenticate to the server.  The
                default value is None

            password (str): The password used to authenticate to the server.
                The default value is None.

            client_id (str): The client_id value to use when authenticating
                to the server using OAuth.  The default value is None

            client_secret (str): The client_secret value to use when
                authenticating to the server using OAuth  The default value
                is None

            timeout (int): The request timeout for sending requests to the
                server.
        """

        self.user = user
        self.password = password

        self.client_id = client_id
        self.client_secret = client_secret

        self.token = None

        self.authenticated = False

        self.client = self._init_client(
            base_url=self._make_base_url(host, port, base_path, use_tls),
            verify=verify,
            timeout=timeout,
        )
        self.client.headers["User-Agent"] = f"ipsdk/{metadata.version}"

    def _make_base_url(
        self,
        host: str,
        port: int = 0,
        base_path: Optional[str] = None,
        use_tls: bool = True,
    ) -> str:
        """
        Join parts of the request to construct a valid URL

        This function will take the request object and join the
        individual parts together to construct a full URL.

        Args:
            host (str): The hostname or IP address of the API endpoint.  This
                argument is required.

            port (int): The port used to connect to the API.  If the value of
                port is 0, the port will be auto determined based on the value
                of use_tls.  When use_tls is True, the value of port will be
                443 and when use_tls is False, the value of port will be 80.
                The default value is 0

            use_tls (bool): Enable or disable TLS support.  When the value is
                set to True, TLS will be enabled on the connection and when
                this value is False, TLS will be disabled.  The default value
                is True

            base_path (str): Base path to prepend when constructing the final
                URL.   The default value is None

        Returns:
            A string that represents the full URL
        """

        if port == 0:
            port = 443 if use_tls is True else 80

        if port not in (None, 80, 443):
            host = f"{host}:{port}"

        base_path = "" if base_path is None else base_path
        proto = "https" if use_tls else "http"

        return urllib.parse.urlunsplit((proto, host, base_path, None, None))

    def _build_request(
        self,
        method: str,
        path: str,
        json: Optional[Union[str, bytes, dict, list]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Request:
        """
        Create a new instance of httpx.Request

        Args:
            method (str): The HTTP method to invoke for this request.  This
                is a required argument

            path (str): The path to the resource.  This value is appended to
                the base URL of the client to generate the full URI.  This
                is a required argument.

            params (dict): A dict object of key value pairs that will be used
                to construct the URL query string.  The default value is
                None

            json (str, bytes, dict, list): The body to include in the request
                as a JSON object.  If the value of json is list or dict, the
                data will be converted to a JSON string.   When this argument
                is set, the "Content-Type" and "Accept" headers will be set
                to "application/json". The default value is None

        Returns:
            A `httpx.Request` object that can be used to send to the server
        """

        headers = {}

        # If the value of json is not None, automatically set the Content-Type
        # and Accept headers to "application/json".  Technically, httpx will do
        # this for us but setting it here to make it very explicit.
        if json is not None:
            logging.debug(
                "automatically setting Content-Type and Accept headers due to json data"
            )
            headers.update(
                {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

        if self.token is not None:
            logging.debug("adding Authorization header to request")
            headers["Authorization"] = f"Bearer {self.token}"

        # The value for the keyword `json` is passed to the httpx build_request
        # function.  If the value is of type list or dict, it will
        # automatically be dumped to a string value and inserted into the body
        # of the request.
        return self.client.build_request(
            method=method,
            url=path,
            params=params,
            headers=headers,
            json=json,
        )

    @abc.abstractmethod
    def _init_client(
        self, base_url: Optional[str] = None, verify: bool = True, timeout: int = 30
    ) -> Union[httpx.Client, httpx.AsyncClient]:
        """
        Abstract method that will initialize the client

        Args:
            base_url (str): The base URL used to prepend to every request. The
                default value is None

            verify (bool): Enable or disable certificate verification.  The
                default value is True

            timeout (int): Sets the connection timeout value for each sent
                request in seconds.  The default value is 30

        Returns:
            A valid httpx client object.
        """


class Connection(ConnectionBase):
    client: httpx.Client  # Override the Union type from base class

    def _init_client(
        self, base_url: Optional[str] = None, verify: bool = True, timeout: int = 30
    ) -> httpx.Client:
        """
        Initialize the httpx.Client instance

        The `httpx.Client` instance provides the connection to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.

        Args:
            base_url (str): The base url to use when crafting requests.  This
                value will be prepended to all requests

            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

            timeout (int): Set the connection timeout value when sending
                requests.  The default value is 30 seconds

        Returns:
            An instance of `httpx.Client`
        """

        logging.info(f"Creating new client for {base_url}")

        return httpx.Client(
            base_url=base_url or "",
            verify=verify,
            timeout=timeout,
        )

    @abc.abstractmethod
    def authenticate(self) -> None:
        """
        Abstract method for implementing authentication
        """

    def _send_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, dict, list]] = None,
    ) -> Response:
        """
        Send will send the request to the API endpoint and return the response

        If the request object provides a body value and the body value is
        either a list or dict object, this method will jsonify the data and
        automatically set the `Content-Type` and `Accept` headers to
        `application/json`.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        if self.authenticated is not True:
            self.authenticate()
            self.authenticated = True

        request = self._build_request(
            method=method,
            path=path,
            params=params,
            json=json,
        )

        try:
            logging.debug(f"{method} {path}")
            res = self.client.send(request)

            # Check for HTTP status errors
            if res.status_code >= HTTPStatus.BAD_REQUEST.value:
                logging.debug(f"HTTP {res.status_code} response from {request.url}")
                raise exceptions.classify_http_error(
                    res.status_code,
                    request_url=str(request.url),
                    response=res
                )

        except httpx.RequestError as exc:
            logging.debug(traceback.format_exc())
            raise exceptions.classify_httpx_error(exc, str(request.url))

        except httpx.HTTPStatusError as exc:
            logging.debug(traceback.format_exc())
            raise exceptions.classify_httpx_error(exc, str(request.url))

        except exceptions.IpsdkError:
            # Re-raise our own exceptions
            raise

        except Exception as exc:
            logging.debug(traceback.format_exc())
            msg = f"Unexpected error occurred: {exc!s}"
            raise exceptions.IpsdkError(
                msg,
                details={"request_url": str(request.url), "original_error": str(exc)},
            )

        return Response(res)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        Send a HTTP GET request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return self._send_request(HTTPMethod.GET.value, path=path, params=params)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        Send a HTTP DELETE request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return self._send_request(HTTPMethod.DELETE.value, path=path, params=params)

    def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, list, dict]] = None,
    ) -> Response:
        """
        Send a HTTP POST request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return self._send_request(
            HTTPMethod.POST.value, path=path, params=params, json=json
        )

    def put(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, list, dict]] = None,
    ) -> Response:
        """
        Send a HTTP PUT request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return self._send_request(
            HTTPMethod.PUT.value, path=path, params=params, json=json
        )

    def patch(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, list, dict]] = None,
    ) -> Response:
        """
        Send a HTTP PATCH request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return self._send_request(
            HTTPMethod.PATCH.value, path=path, params=params, json=json
        )


class AsyncConnection(ConnectionBase):
    client: httpx.AsyncClient  # Override the Union type from base class

    def _init_client(
        self, base_url: Optional[str] = None, verify: bool = True, timeout: int = 30
    ) -> httpx.AsyncClient:
        """
        Initialize the httpx.AsyncClient instance

        The `httpx.AsyncClient` instance provides the connection to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.

        Args:
            base_url (str): The base URL used to prepend to every request

            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

            timeout (int): Set the connection timeout value to be used for
                each request in seconds.  The default value is 30.

        Returns:
            An instance of `httpx.AsyncClient`
        """

        logging.info(f"Creating new async client for {base_url}")

        return httpx.AsyncClient(
            base_url=base_url or "", verify=verify, timeout=timeout
        )

    @abc.abstractmethod
    async def authenticate(self) -> None:
        pass

    async def _send_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, dict, list]] = None,
    ) -> Response:
        """
        Send will send the request to the API endpoint and return the response

        If the request object provides a body value and the body value is either
        a list or dict object, this method will jsonify the data and
        automatically set the `Content-Type` and `Accept` headers to
        `application/json`.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        if self.authenticated is False:
            await self.authenticate()
            self.authenticated = True

        request = self._build_request(
            method=method,
            path=path,
            params=params,
            json=json,
        )

        try:
            res = await self.client.send(request)

            # Check for HTTP status errors
            if res.status_code >= HTTPStatus.BAD_REQUEST.value:
                logging.debug(f"HTTP {res.status_code} response from {request.url}")
                raise exceptions.classify_http_error(
                    res.status_code,
                    request_url=str(request.url),
                    response=res
                )

        except httpx.RequestError as exc:
            logging.debug(traceback.format_exc())
            sdk_exc = exceptions.classify_httpx_error(exc, str(request.url))
            raise sdk_exc

        except httpx.HTTPStatusError as exc:
            logging.debug(traceback.format_exc())
            sdk_exc = exceptions.classify_httpx_error(exc, str(request.url))
            raise sdk_exc

        except exceptions.IpsdkError:
            # Re-raise our own exceptions
            raise

        except Exception as exc:
            logging.debug(traceback.format_exc())
            msg = f"Unexpected error occurred: {exc!s}"
            raise exceptions.IpsdkError(
                msg,
                details={"request_url": str(request.url), "original_error": str(exc)},
            )

        return Response(res)

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        Send a HTTP GET request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return await self._send_request(HTTPMethod.GET.value, path=path, params=params)

    async def delete(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Send a HTTP DELETE request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.DELETE.value, path=path, params=params
        )

    async def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, dict, list]] = None,
    ) -> Response:
        """
        Send a HTTP POST request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.POST.value, path=path, params=params, json=json
        )

    async def put(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, dict, list]] = None,
    ) -> Response:
        """
        Send a HTTP PUT request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.PUT.value, path=path, params=params, json=json
        )

    async def patch(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[str, bytes, dict, list]] = None,
    ) -> Response:
        """
        Send a HTTP PATCH request to the server and return the response.

        Args:
            method (HTTPMethod): The HTTP method to call when sending this
                request to the server.  This argument is required.

            path (str): The URI path to use for this request.  This value
                will be combined with the client's base_url to create the full
                path to the resource.  This argument is required.

            params (dict): The set of key value pairs as a dict object used
                to construct the query string for the request.  The default
                value of params is None

            json: (str, bytes, dict, list): The JSON payload to include in
                the request when sent to the server.  The value must either be
                a string representation of a JSON object or a dict or list
                object that can be converted to a valid JSON string.  The
                default value for json is None

        Returns:
            A `Response` object
        """
        return await self._send_request(
            HTTPMethod.PATCH.value, path=path, params=params, json=json
        )
