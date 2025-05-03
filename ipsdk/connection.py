# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import abc
import traceback

import urllib.parse

import httpx

from . import logger
from . import metadata


class HTTPMethod:
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"


class ConnectionBase(object):

    def __init__(self, host, port=0, base_path=None, use_tls=True, verify=True, user=None, password=None, client_id=None, client_secret=None, timeout=30):
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

    def _make_base_url(self, host: str, port: int=0,
                       base_path: str=None, use_tls: bool=True) -> str:
        """
        Join parts of the request to construct a valid URL

        This function will take the request object and join the
        individual parts together to cnstruct a full URL.

        Args:
            host (str): The hostname or IP address of the API endpoint
            port (int): The port used to connect to the API
            use_tls (bool): Enable or disable TLS support
            base_path (str): Base path to prepend when consructing the final URI

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
        url: str,
        data: [str, bytes, dict, list]=None,
        params: dict=None
    ) -> httpx.Request:
        """
        Create a new instance of httpx.Request
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        return self.client.build_request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    @abc.abstractmethod
    def _init_client(self, base_url, verify):
        """
        Abstract method that will initialize the client
        """
        pass


class Connection(ConnectionBase):

    def _init_client(self, base_url, verify: bool=True) -> httpx.Client:
        """
        Initialize the httpx.Client instance

        The `httpx.Client` instance provides the conenction to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.  This
        method is called from `__init__` for the Connection instance

        Args:
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
        pass

    def send_request(self, method: HTTPMethod, url: str, params: dict=None, data: [str, bytes, dict, list]=None) -> httpx.Response:
        """
        Send will send the request to the API endpoint and return the response

        If the request object provides a body value and the body value is
        either a list or dict object, this method will jsonify the data and
        automatically set the `Content-Type` and `Accept` headers to
        `application/json`.

        Args:
            request (Request): A `Request` object used to construct the HTTP
                API call

        Returns:
            A `Response` object
        """

        if self.authenticated is not True:
            self.authenticate()
            self.authenticated = True

        request = self._build_request(
            method=method,
            url=url,
            data=data,
            params=params
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

    def get(self, path, params=None):
        return self.send_request(HTTPMethod.GET, url=path, params=params)

    def delete(self, path, params=None):
        return self.send_request(HTTPMethod.DELETE, url=path, params=params)

    def post(self, path, data=None, params=None):
        return self.send_request(HTTPMethod.POST, url=path, params=params, data=data)

    def put(self, path, data=None, params=None):
        return self.send_request(HTTPMethod.PUT, url=path, params=params, data=data)

    def patch(self, path, data=None, params=None):
        return self.send_request(HTTPMethod.PATCH, url=path, params=params, data=data)



class AsyncConnection(ConnectionBase):

    def _init_client(self, base_url, verify: bool=True) -> httpx.AsyncClient:
        """
        Initialize the httpx.Client instance

        The `httpx.Client` instance provides the conenction to the server
        for sending requests and receiving responses.   This method will
        initialize the client and return it to the calling function.  This
        method is called from `__init__` for the Connection instance

        Args:
            verify (bool): Enable or disable the validation of certificates
                when connecting to a server over TLS

        Returns:
            An instance of `httpx.Client`
        """

        logger.info(f"Creating new async client for {base_url}")

        return httpx.AsyncClient(
            base_url=base_url,
            verify=verify
        )

    @abc.abstractmethod
    async def authenticate(self):
        pass

    async def send_request(self, method: HTTPMethod, url: str, params: dict=None, data: [str, bytes, dict, list]=None) -> httpx.Response:
        """
        Send will send the request to the API endpoint and return the response

        If the request object provides a body value and the body value is either
        a list or dict object, this method will jsonify the data and
        automatically set the `Content-Type` and `Accept` headers to
        `application/json`.

        Args:
            request (Request): A `Request` object used to construct the HTTP
                API call

        Returns:
            A `Response` object
        """
        if self.authenticated is False:
            await self.authenticate()
            self.authenticated = True

        request = self._build_request(
            method=method,
            url=url,
            data=data,
            params=params,
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

    async def get(self, path, params=None):
        return await self.send_request(HTTPMethod.GET, url=path, params=params)

    async def delete(self, path, params=None):
        return await self.send_request(HTTPMethod.DELETE, url=path, params=params)

    async def post(self, path, data=None, params=None):
        return await self.send_request(HTTPMethod.POST, url=path, params=params, data=data)

    async def put(self, path, data=None, params=None):
        return await self.send_request(HTTPMethod.PUT, url=path, params=params, data=data)

    async def patch(self, path, data=None, params=None):
        return await self.send_request(HTTPMethod.PATCH, url=path, params=params, data=data)
