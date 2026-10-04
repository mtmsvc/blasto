import pytest
from fastapi.testclient import TestClient

from blasto.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
