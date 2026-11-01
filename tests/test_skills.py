from fastapi.testclient import TestClient


def test_create_skill(client: TestClient) -> None:
    response = client.post("/skills", json={"name": "Python", "category": "language", "level": 4})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Python", "category": "language", "level": 4}


def test_create_skill_defaults(client: TestClient) -> None:
    response = client.post("/skills", json={"name": "Teamwork"})

    assert response.status_code == 201
    assert response.json()["category"] == "other"
    assert response.json()["level"] is None


def test_duplicate_skill_returns_409(client: TestClient) -> None:
    client.post("/skills", json={"name": "Python"})

    response = client.post("/skills", json={"name": "Python"})

    assert response.status_code == 409


def test_invalid_level_returns_422(client: TestClient) -> None:
    response = client.post("/skills", json={"name": "Go", "level": 9})

    assert response.status_code == 422


def test_list_skills(client: TestClient) -> None:
    client.post("/skills", json={"name": "Rust"})
    client.post("/skills", json={"name": "Docker", "category": "tool"})

    response = client.get("/skills")

    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["Docker", "Rust"]
