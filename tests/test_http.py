# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk.http import make_url, Request, Response, Connection


class DummyConnection(Connection):
    def authenticate(self):
        self.authenticated = True


def test_make_url_with_defaults():
    url = make_url("example.com", "/test")
    assert url.startswith("https://")
    assert "example.com" in url
    assert "test" in url


def test_make_url_with_base_path():
    url = make_url("example.com", "endpoint", base_path="/api")
    assert "api/endpoint" in url


def test_request_dataclass():
    req = Request(method="POST", path="/test", body={"key": "val"})
    assert req.method == "POST"
    assert req.path == "/test"
    assert isinstance(req.body, dict)


def test_response_dataclass():
    res = Response(status_code=200, status="OK", body="data", headers={"X-Test": "yes"})
    assert res.status_code == 200
    assert res.status == "OK"
    assert res.body == "data"
    assert res.headers["X-Test"] == "yes"


def test_connection_send_sets_headers_and_auth(monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            status_code = 200
            reason_phrase = "OK"
            headers = {}
            text = "{}"
            elapsed = ".1"
            def raise_for_status(self): pass
        return MockResponse()

    dummy = DummyConnection("localhost", base_path="/api", verify=False)
    dummy.token = "abc123"
    dummy.authenticated = True
    monkeypatch.setattr(dummy.client, "request", mock_post)

    request = Request(method="GET", path="/test")
    resp = dummy.send(request)
    assert resp.status_code == 200
    assert resp.status == "OK"
