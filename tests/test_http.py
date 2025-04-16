# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk.http import (
    make_url,
    Response,
    Request,
    Connection,
)

class DummyConnection(Connection):
    def authenticate(self):
        self.authenticated = True

def test_make_url_https():
    url = make_url("example.com", "/api/test", use_tls=True)
    assert url.startswith("https://")

def test_make_url_http():
    url = make_url("example.com", "api/test", port=8080, use_tls=False)
    assert url.startswith("http://") and ":8080" in url

def test_request_response_classes():
    resp = Response(headers={}, body=b"{}", status_code=200, status="OK")
    assert isinstance(resp, Response)
    req = Request(method="POST", path="/api", body=b"{}", headers={})
    assert isinstance(req, Request)

def test_connection_get(monkeypatch):
    conn = DummyConnection("example.com")
    monkeypatch.setattr(conn, "send", lambda req: Response(headers={}, body=b"{}", status_code=200, status="OK"))
    resp = conn.get("/path")
    assert resp.status_code == 200
