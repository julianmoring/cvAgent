from fastapi.testclient import TestClient

REQUEST = {"title": "Backend role", "description": "Looking for a Python developer"}


def test_create_project_request_is_pending(client: TestClient) -> None:
    response = client.post("/project-requests", json=REQUEST)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["title"] == "Backend role"
    assert body["created_at"]


def test_get_project_request(client: TestClient) -> None:
    created = client.post("/project-requests", json=REQUEST).json()

    response = client.get(f"/project-requests/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_unknown_project_request_returns_404(client: TestClient) -> None:
    response = client.get("/project-requests/999")

    assert response.status_code == 404


def test_empty_title_returns_422(client: TestClient) -> None:
    response = client.post("/project-requests", json={**REQUEST, "title": ""})

    assert response.status_code == 422
