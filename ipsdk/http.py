# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import abc
import logging
import traceback
import functools

import urllib.parse

from dataclasses import dataclass, field
from typing import Union

import requests

logger = logging.getLogger(__name__)


def send_request(method, url, headers=None, data=None, params=None, auth=None, timeout=None,
                certificate_file=None, private_key_file=None, verify=None, disable_warnings=None,
                session=None) -> requests.Response:
    """ Send the request to the host and return the response

    This function sends the request to the host and waits for the
    response.  The raw response object is returned to the calling
    function.

    Args:
        method (str): The HTTP method for the request
        url (str): The full HTTP URL to send the request to
        headers (dict): A dictionary that contains any headers to include
            in the request
        data (bytes): A byte array to include in the body of the HTTP
            API request
        params (dict): A dictionary that cotains one or more values used
            to construct a query string to include with the request
        auth (typing.Any): A `requests` auth object
        timeout (int): Configures the timeout for waiting for a response
            from the remote API
        verify (bool): Enable or disable certificate validation
        disable_warnings (bool): Enable or disable `urllib3` warnings
        session (requests.Session): A `requests.Session` object

    Returns
        A `Response` object that contains the response from the API call
    """
    kwargs = {
        "method": method,
        "url": url,
        "headers": headers,
        "params": params,
        "verify": verify,
        "timeout": timeout,
    }

    if auth is not None:
        kwargs["auth"] = auth

    if timeout is not None:
        kwargs["timeout"] = timeout

    if certificate_file is not None and private_key_file is not None:
        kwargs["cert"] = (certificate_file, private_key_file)

    if data is not None:
        kwargs["data"] = data

    logger.debug(f"Request object: {kwargs}")

    try:
        if session is not None:
            resp = session.request(**kwargs)
        else:
            resp = requests.request(**kwargs)

        logger.info(f"HTTP response is {resp.status_code} {resp.reason}")
        logger.debug(f"Start of response body\n{resp.text}\nEnd of response body")
        logger.debug(f"Call completed in {resp.elapsed}")

    except requests.exceptions.ConnectionError:
        logger.debug(traceback.format_exc())
        raise ValueError(f"Failed to establish a connection to {url}")

    except Exception as exc:
        logger.debug(traceback.format_exc())
        raise ValueError(str(exc))

    return resp


get = functools.partial(send_request, "GET")
post = functools.partial(send_request, "POST")
put = functools.partial(send_request, "PUT")
delete = functools.partial(send_request, "DELETE")
patch = functools.partial(send_request, "PATCH")


def make_url(host, path, base_path=None, port=0, use_tls=True) -> str:
    """ Join parts of the request to construct a valid URL

    This function will take the request object and join the
    individual parts together to cnstruct a full URL.

    Args:
        host (str): The hostname or IP address of the API endpoint
        port (int): The port used to connect to the API
        path (str): The URI path of the endpoint
        use_tls (bool): Enable or disable TLS support
        base_path (str): Base path to prepend when consructing the final URI

    Returns:
        A string that represents the full URL
    """
    if port == 0:
        port = 443 if use_tls is True else 80

    if port not in (None, 80, 443):
        host = f"{host}:{port}"

    if path[0] == "/":
        path = path[1:]

    if base_path is not None:
        if base_path[0] == "/":
            base_path = base_path[1:]
        uri = f"{base_path}/{path}"
    else:
        uri = path

    path = urllib.parse.quote(uri)

    proto = "https" if use_tls else "http"

    return urllib.parse.urlunsplit((proto, host, uri, None, None))

@dataclass
class Response(object):
    """ Response respresents a response from an HTTP request

    The Response object provides access to the response from
    a HTTP request that includes the body of the response, response
    status and header information.

    Args:
        headers (dict): Set of key/value pairs returned from the API call

        body (bytes): The body of the response

        status_code (int): The HTTP status code in the response

        status (str):  The HTTP status text in the response
    """
    headers: dict
    body: bytes
    status_code: int
    status: str


@dataclass
class Request(object):
    """Request represents an HTTP request

    The Request object represents an HTTP request to be sent
    to an API endpoint.  The Request object is used to create
    and send an API call.

    Args:
        method (str): The HTTP method to invoke.  Valid values include
            `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.

        path (str): The URI to send the request to.  The URI will be
            combined with the `host` and `port` to construct the full
            URL to send the request to.

        body (bytes): The body of the HTTP request.

        headers (dict): The HTTP headers to set in the API request

        disable_warnings (bool): Enable or disable Python warnings
            generated by urllib3

    """
    method: str = "GET"
    path: str = None
    body: Union[dict, list, str] = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    disable_warnings: bool = True


class Connection(object):

    def __init__(self, host, port=0, base_path=None, use_tls=True, verify=True, user=None, password=None, client_id=None, client_secret=None, timeout=30):
        self.host = host
        self.port = port
        self.base_path = base_path
        self.use_tls = use_tls
        self.verify = verify
        self.user = user
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.token = None
        self.session = requests.Session()
        self.authenticated = False

    def send(self, request) -> Response:
        """Send will send the request to the API endpoint and return the response

        Args:
            request (Request): A `Request` object used to construct the HTTP
                API call

        Returns:
            A `Response` object
        """
        if self.authenticated is not True:
            self.authenticate()

        url = make_url(
            self.host,
            request.path,
            base_path=self.base_path,
            port=self.port,
            use_tls=self.use_tls,
        )

        headers = request.headers

        if isinstance(request.body, (dict, list)):
            headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        resp = send_request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.body,
            params=request.params,
            verify=self.verify,
            disable_warnings=request.disable_warnings,
            session=self.session
        )

        return Response(
            status_code=resp.status_code,
            status=resp.reason,
            headers=resp.headers,
            body=resp.text
        )

    @abc.abstractmethod
    def authenticate(self):
        pass

    def get(self, path, params=None):
        return self.send(Request(method="GET", path=path, params=params))

    def delete(self, path, params=None):
        return self.send(Request(method="DELETE", path=path, params=params))

    def post(self, path, body=None, params=None):
        return self.send(Request(method="POST", path=path, body=body, params=params))

    def put(self, path, body=None, params=None):
        return self.send(Request(method="PUT", path=path, body=body, params=params))

    def patch(self, path, body=None, params=None):
        return self.send(Request(method="PATCH", path=path, body=body, params=params))
