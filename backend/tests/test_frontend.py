"""Single-server mode: FastAPI serves the built frontend next to the API.

Each test passes its own dist folder (or none), so the result never depends on
whether the developer has run `npm run build`.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app

INDEX = "<!doctype html><title>EcoScan</title><div id=root></div>"


def make_client(frontend_dist) -> TestClient:
    app = create_app(frontend_dist=frontend_dist)
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    return TestClient(app)


@pytest.fixture
def dist(tmp_path):
    folder = tmp_path / "dist"
    (folder / "assets").mkdir(parents=True)
    (folder / "index.html").write_text(INDEX)
    (folder / "assets" / "app.js").write_text("console.log('ecoscan')")
    (folder / "favicon.svg").write_text("<svg></svg>")
    (tmp_path / "secret.txt").write_text("outside dist")
    return folder


@pytest.fixture
def client(dist):
    return make_client(dist)


def test_root_serves_index_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.text == INDEX


@pytest.mark.parametrize("path, content_type, body", [
    ("/assets/app.js", "javascript", "console.log('ecoscan')"),
    ("/favicon.svg", "image/svg+xml", "<svg></svg>"),
])
def test_built_files_are_served(client, path, content_type, body):
    response = client.get(path)

    assert response.status_code == 200
    assert content_type in response.headers["content-type"]
    assert response.text == body


def test_unknown_page_falls_back_to_index_html(client):
    response = client.get("/results/some-scan")

    assert response.status_code == 200
    assert response.text == INDEX


def test_missing_asset_is_a_404_not_html(client):
    response = client.get("/assets/old-build.js")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


# Encoded, because the HTTP client would tidy a plain "/../" away before sending it.
@pytest.mark.parametrize("path", ["/%2e%2e/secret.txt", "/..%2fsecret.txt", "/%2e%2e%2fsecret.txt"])
def test_files_outside_dist_are_never_served(client, path):
    response = client.get(path)

    assert response.status_code == 404
    assert "outside dist" not in response.text


def test_api_still_works(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.post("/api/score", json={"items": [{"category": "jeans", "condition": "second-hand"}]})
    assert response.status_code == 200
    assert response.json()["total_points"] == 80


@pytest.mark.parametrize("method, path, status", [
    ("GET", "/api/does-not-exist", 404),
    ("GET", "/api", 404),
    ("POST", "/api/does-not-exist", 404),
    ("POST", "/api/health", 405),  # wrong method on a real route, as before
])
def test_api_errors_stay_json_not_index_html(client, method, path, status):
    response = client.request(method, path)

    assert response.status_code == status
    assert "detail" in response.json()


def test_api_docs_are_still_served(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").json()["paths"].keys() >= {"/api/health", "/api/analyze"}


def test_post_to_a_page_is_not_given_index_html(client):
    assert client.post("/").status_code == 404


@pytest.mark.parametrize("frontend_dist", ["missing", None])
def test_without_a_built_frontend_only_the_api_is_served(tmp_path, frontend_dist, caplog):
    caplog.set_level("INFO", logger="app.main")
    client = make_client(tmp_path / "dist" if frontend_dist == "missing" else None)

    assert client.get("/").status_code == 404
    assert client.get("/api/health").json() == {"status": "ok"}
    assert "npm run build" in caplog.text
