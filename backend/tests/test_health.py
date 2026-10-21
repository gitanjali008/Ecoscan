from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    

def test_unknown_route_returns_404():
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404


def test_root_redirects_to_the_api_docs():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
    assert client.get("/").status_code == 200  # the docs page itself loads


def test_root_is_not_in_the_api_schema():
    paths = client.get("/openapi.json").json()["paths"]

    assert "/" not in paths
