# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import abc
import traceback

import urllib.parse

from typing import Union

import httpx

from . import logger
from . import metadata


class HTTPMethod:
    """
    The HTTPMethod class acts as an enum for specifying the HTTP method to use
    when constructing requests
    """
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"


class ConnectionBase(object):

    def __init__(self,
                 host: str,
                 port: int=0,
                 base_path: str=None,
                 use_tls: bool=True,
                 verify: bool=True,
                 user: str=None,
                 password: str=None,
                 client_id: str=None,
                 client_secret: str=None,
                 timeout: int=30):
        """
        Base class for all connection classes

        ConnectionBase is the base connection type that all connection classes
        are derived from.  It provides a set of common proprties used by both
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
        )
        self.client.headers["User-Agent"] = f"ipsdk/{metadata.version}"

    def _make_base_url(self, host: str,
                       port: int=0,
                       base_path: str=None,
                       use_tls: bool=True) -> str:
        """
        Join parts of the request to construct a valid URL

        This function will take the request object and join the
        individual parts together to cnstruct a full URL.

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

            base_path (str): Base path to prepend when consructing the final
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

    def _build_request(self,
                       method: str,
                       path: str,
                       json: [str, bytes, dict, list]=None,
                       params: dict=None) -> httpx.Request:
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
            logger.debug("automatically setting Content-Type and Accept headers due to json data")
            headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })

        if self.token is not None:
            logger.debug("adding Authorization header to request")
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
    def _init_client(self, base_url: str=None, verify: bool=True):
        """
        Abstract method that will initialize the client

        Args:
            base_url (str): The base URL used to prepend to every request. The
                default value is None

            verify (bool): Enable or disable certificate verification.  The
                default value is True

        Returns:
            A valid httpx client object.
        """
        pass


class Connection(ConnectionBase):

    def _init_client(self, base_url: str=None, verify: bool=True) -> httpx.Client:
        """
        Initialize the httpx.Client instance

        The `httpx.Client` instance provides the conenction to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.

        Args:
            base_url (str): The base url to use when crafting requests.  This
                value will be prepended to all requests

            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

        Returns:
            An instance of `httpx.Client`
        """

        logger.info(f"Creating new client for {base_url}")

        return httpx.Client(
            base_url=base_url,
            verify=verify,
        )

    @abc.abstractmethod
    def authenticate(self):
        """
        Abstract method for implementing authentication
        """
        pass

    def _send_request(self,
                      method: HTTPMethod,
                      path: str,
                      params: dict=None,
                      json: [str, bytes, dict, list]=None) -> httpx.Response:
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
            A `httpx.Response` object
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
            res = self.client.send(request)
            res.raise_for_status()

        except httpx.RequestError as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"An error occurred while requesting {exc.request.url!r}.")

        except httpx.HTTPStatusError as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")

        except Exception as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"unknown error occurred: {str(exc)}")

        return res

    def get(self, path: str, params: dict=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return self._send_request(HTTPMethod.GET, path=path, params=params)

    def delete(self, path: str, params: dict=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return self._send_request(HTTPMethod.DELETE, path=path, params=params)

    def post(self, path: str, params: dict=None, json: Union[str, bytes, list, dict]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return self._send_request(HTTPMethod.POST, path=path, params=params, json=json)

    def put(self, path: str, params: dict=None, json: Union[str, bytes, list, dict]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return self._send_request(HTTPMethod.PUT, path=path, params=params, json=json)

    def patch(self, path: str, params: dict=None, json: Union[str, bytes, list, dict]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return self._send_request(HTTPMethod.PATCH, path=path, params=params, json=json)


class AsyncConnection(ConnectionBase):

    def _init_client(self, base_url: str=None, verify: bool=True) -> httpx.AsyncClient:
        """
        Initialize the httpx.AsyncClient instance

        The `httpx.AsyncClient` instance provides the conenction to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.

        Args:
            base_url (str): The base URL used to prepend to every request

            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

        Returns:
            An instance of `httpx.AsyncClient`
        """

        logger.info(f"Creating new async client for {base_url}")

        return httpx.AsyncClient(
            base_url=base_url,
            verify=verify
        )

    @abc.abstractmethod
    async def authenticate(self):
        pass

    async def _send_request(self,
                            method: HTTPMethod,
                            path: str,
                            params: dict=None,
                            json: [str, bytes, dict, list]=None) -> httpx.Response:
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
            res.raise_for_status()

        except httpx.RequestError as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"An error occurred while requesting {exc.request.url!r}.")

        except httpx.HTTPStatusError as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")

        except Exception as exc:
            logger.debug(traceback.format_exc())
            raise ValueError(f"unknown error occurred: {str(exc)}")

        return res

    async def get(self, path: str, params: dict=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return await self._send_request(HTTPMethod.GET, url=path, params=params)

    async def delete(self, path: str, params: dict=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return await self._send_request(HTTPMethod.DELETE, url=path, params=params)

    async def post(self, path: str, params: dict=None, json: Union[str, bytes, dict, list]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return await self._send_request(HTTPMethod.POST, url=path, params=params, json=json)

    async def put(self, path: str, params: dict=None, json: Union[str, bytes, dict, list]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return await self._send_request(HTTPMethod.PUT, url=path, params=params, json=json)

    async def patch(self, path: str, params: dict=None, json: Union[str, bytes, dict, list]=None) -> httpx.Response:
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
            A `httpx.Response` object
        """
        return await self._send_request(HTTPMethod.PATCH, url=path, params=params, json=json)
