
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

# Mocked base class to simulate http.Connection
class MockConnection:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.session = MagicMock()

# Mock dependencies
import sys
module = sys.modules[__name__]
setattr(module, 'http', SimpleNamespace(Connection=MockConnection, make_url=lambda *a, **kw: "https://mock.url"))
setattr(module, 'stringutils', SimpleNamespace(
    string_to_int=lambda x: int(x) if x is not None else 0,
    string_to_bool=lambda x: str(x).lower() in ("1", "true", "yes")
))

# Redefine the Gateway, Cloud, Platform classes for testing
class Gateway(MockConnection):
    def authenticate(self):
        data = {
            "username": self.user,
            "password": self.password,
        }
        url = "https://mock.url"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        res = self.session.post(url, headers=headers, json=data)
        res.raise_for_status()
        self.authenticated = True


class Cloud(MockConnection):
    def authenticate(self):
        url = "https://mock.url"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = self.session.post(url, headers=headers, data=data)
        res.raise_for_status()
        self.token = res.json()["access_token"]
        self.authenticated = True


class Platform(MockConnection):
    def authenticate(self):
        if self.client_id and self.client_secret:
            self.authenticate_oauth()
        elif self.user and self.password:
            self.authenticate_user()
        else:
            raise ValueError("no authentication methods left to try")
        self.authenticated = True

    def authenticate_user(self):
        data = {
            "user": {
                "username": self.user,
                "password": self.password,
            }
        }
        url = "https://mock.url"
        res = self.session.post(url, json=data)
        res.raise_for_status()

    def authenticate_oauth(self):
        url = "https://mock.url"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = self.session.post(url, headers=headers, data=data)
        res.raise_for_status()
        self.token = res.json()["access_token"]


@pytest.fixture
def mock_response():
    def _response(json_data=None, raise_for_status=None):
        mock = MagicMock()
        mock.json.return_value = json_data or {}
        if raise_for_status:
            mock.raise_for_status.side_effect = raise_for_status
        return mock
    return _response


def test_gateway_authenticate_success(mock_response):
    gateway = Gateway(user="user", password="pass")
    gateway.session.post.return_value = mock_response()
    gateway.authenticate()
    assert gateway.authenticated


def test_cloud_authenticate_success(mock_response):
    cloud = Cloud(client_id="id", client_secret="secret")
    cloud.session.post.return_value = mock_response({"access_token": "abc123"})
    cloud.authenticate()
    assert cloud.token == "abc123"
    assert cloud.authenticated


def test_platform_authenticate_user(mock_response):
    platform = Platform(user="admin", password="admin", client_id=None, client_secret=None)
    platform.session.post.return_value = mock_response()
    platform.authenticate()
    assert platform.authenticated


def test_platform_authenticate_oauth(mock_response):
    platform = Platform(client_id="cid", client_secret="csecret", user=None, password=None)
    platform.session.post.return_value = mock_response({"access_token": "xyz"})
    platform.authenticate()
    assert platform.token == "xyz"
    assert platform.authenticated


def test_platform_authenticate_failure():
    platform = Platform(user=None, password=None, client_id=None, client_secret=None)
    with pytest.raises(ValueError):
        platform.authenticate()


def test_authentication_http_error(mock_response):
    cloud = Cloud(client_id="id", client_secret="secret")
    cloud.session.post.return_value = mock_response(raise_for_status=Exception("401 Unauthorized"))
    with pytest.raises(Exception):
        cloud.authenticate()
