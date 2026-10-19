from fastapi.testclient import TestClient

ADMIN_HEADERS = {
    "X-API-Key": "test-admin-key"
}  # matches ADMIN_API_KEY in pyproject.toml

APPLICATION = {
    "name": "Jānis Bērziņš",
    "phone": "+371 20000000",
    "email": "janis@example.com",
    "training_type": "online",
    "cat_b": True,
}


def test_create_and_get_application(client: TestClient) -> None:
    created = client.post("/applications", json=APPLICATION)
    assert created.status_code == 201
    application_id = created.json()["id"]

    response = client.get(f"/applications/{application_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["name"] == "Jānis Bērziņš"
    assert response.json()["cat_b"] is True
    assert response.json()["cat_a"] is False  # filled in by the server default


def test_list_applications(client: TestClient) -> None:
    client.post("/applications", json=APPLICATION)
    client.post("/applications", json=APPLICATION)

    response = client.get("/applications", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 2  # exactly 2: the table was empty before this test


def test_update_application(client: TestClient) -> None:
    application_id = client.post("/applications", json=APPLICATION).json()["id"]

    response = client.put(
        f"/applications/{application_id}",
        json={**APPLICATION, "name": "Anna"},
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Anna"


def test_delete_application(client: TestClient) -> None:
    application_id = client.post("/applications", json=APPLICATION).json()["id"]

    assert (
        client.delete(
            f"/applications/{application_id}", headers=ADMIN_HEADERS
        ).status_code
        == 200
    )
    assert (
        client.get(f"/applications/{application_id}", headers=ADMIN_HEADERS).status_code
        == 404
    )


def test_missing_application_returns_error_json(client: TestClient) -> None:
    response = client.get("/applications/999", headers=ADMIN_HEADERS)
    assert response.status_code == 404
    assert response.json() == {
        "error": "application_not_found",
        "message": "Application 999 not found",
    }


def test_admin_endpoints_require_api_key(client: TestClient) -> None:
    assert client.get("/applications").status_code == 401
    assert (
        client.get("/applications", headers={"X-API-Key": "wrong"}).status_code == 401
    )


def test_invalid_training_type_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/applications", json={**APPLICATION, "training_type": "car"}
    )
    assert response.status_code == 422
