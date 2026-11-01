from fastapi.testclient import TestClient

PROJECT = {"name": "Portfolio", "description": "Personal site", "role": "Lead"}


def make_experience(client: TestClient) -> int:
    response = client.post(
        "/experiences",
        json={
            "company": "Acme",
            "role": "Dev",
            "description": "Work",
            "start_date": "2022-01-01",
        },
    )
    return int(response.json()["id"])


def test_create_project_with_skills(client: TestClient) -> None:
    client.post("/skills", json={"name": "FastAPI"})

    response = client.post("/projects", json={**PROJECT, "skills": ["FastAPI"]})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Portfolio"
    assert body["experience"] is None
    assert [s["name"] for s in body["skills"]] == ["FastAPI"]


def test_create_project_with_experience(client: TestClient) -> None:
    experience_id = make_experience(client)

    response = client.post("/projects", json={**PROJECT, "experience_id": experience_id})

    assert response.status_code == 201
    assert response.json()["experience"] == {"id": experience_id, "company": "Acme", "role": "Dev"}


def test_unknown_experience_returns_422(client: TestClient) -> None:
    response = client.post("/projects", json={**PROJECT, "experience_id": 999})

    assert response.status_code == 422


def test_unknown_skill_returns_422(client: TestClient) -> None:
    response = client.post("/projects", json={**PROJECT, "skills": ["Nope"]})

    assert response.status_code == 422


def test_end_date_before_start_returns_422(client: TestClient) -> None:
    dates = {"start_date": "2024-05-01", "end_date": "2024-01-01"}

    response = client.post("/projects", json={**PROJECT, **dates})

    assert response.status_code == 422


def test_list_projects_returns_skills(client: TestClient) -> None:
    client.post("/skills", json={"name": "Docker"})
    client.post("/projects", json={**PROJECT, "skills": ["Docker"]})
    client.post("/projects", json={"name": "Other", "description": "x"})

    response = client.get("/projects")

    assert response.status_code == 200
    body = response.json()
    assert [p["name"] for p in body] == ["Portfolio", "Other"]
    assert [s["name"] for s in body[0]["skills"]] == ["Docker"]
