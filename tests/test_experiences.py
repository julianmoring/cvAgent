from fastapi.testclient import TestClient

EXPERIENCE = {
    "company": "Acme",
    "role": "Backend Developer",
    "description": "Built APIs",
    "start_date": "2022-01-01",
    "end_date": "2024-06-30",
}


def test_create_experience_with_skills(client: TestClient) -> None:
    client.post("/skills", json={"name": "C#"})
    client.post("/skills", json={"name": "SQL"})

    response = client.post("/experiences", json={**EXPERIENCE, "skills": ["C#", "SQL"]})

    assert response.status_code == 201
    body = response.json()
    assert body["company"] == "Acme"
    assert sorted(s["name"] for s in body["skills"]) == ["C#", "SQL"]


def test_create_experience_without_skills(client: TestClient) -> None:
    response = client.post("/experiences", json=EXPERIENCE)

    assert response.status_code == 201
    assert response.json()["skills"] == []


def test_unknown_skill_returns_422(client: TestClient) -> None:
    response = client.post("/experiences", json={**EXPERIENCE, "skills": ["Nope"]})

    assert response.status_code == 422


def test_end_date_before_start_returns_422(client: TestClient) -> None:
    response = client.post("/experiences", json={**EXPERIENCE, "end_date": "2021-01-01"})

    assert response.status_code == 422


def test_list_experiences_returns_skills(client: TestClient) -> None:
    client.post("/skills", json={"name": "Python"})
    client.post("/experiences", json={**EXPERIENCE, "skills": ["Python"]})
    newer = {**EXPERIENCE, "company": "Newer", "start_date": "2024-07-01", "end_date": None}
    client.post("/experiences", json=newer)

    response = client.get("/experiences")

    assert response.status_code == 200
    body = response.json()
    assert [e["company"] for e in body] == ["Newer", "Acme"]
    assert [s["name"] for s in body[1]["skills"]] == ["Python"]
