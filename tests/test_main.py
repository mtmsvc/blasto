import pytest
from fastapi.testclient import TestClient

from blasto.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("name, capitalized_name", [("john", "John"), ("John", "John")])
def test_hello(client: TestClient, name: str, capitalized_name: str) -> None:
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello, {capitalized_name}!"}
