def test_list_submissions_requires_api_key(client):
    response = client.get("/api/submissions")
    assert response.status_code == 401


def test_list_submissions_rejects_wrong_key(client):
    response = client.get("/api/submissions", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_list_submissions_with_valid_key(client):
    client.post(
        "/api/contact",
        json={"name": "Jane Doe", "email": "jane@example.com", "message": "Hello!"},
    )

    response = client.get("/api/submissions", headers={"X-API-Key": "test-admin-key"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Jane Doe"
    assert body[0]["email"] == "jane@example.com"


def test_honeypot_submission_is_not_stored(client):
    client.post(
        "/api/contact",
        json={
            "name": "Spam Bot",
            "email": "bot@example.com",
            "message": "buy my stuff",
            "bot-field": "filled-in",
        },
    )

    response = client.get("/api/submissions", headers={"X-API-Key": "test-admin-key"})

    assert response.json() == []


def test_list_submissions_most_recent_first(client):
    client.post(
        "/api/contact",
        json={"name": "First", "email": "first@example.com", "message": "one"},
    )
    client.post(
        "/api/contact",
        json={"name": "Second", "email": "second@example.com", "message": "two"},
    )

    response = client.get("/api/submissions", headers={"X-API-Key": "test-admin-key"})

    body = response.json()
    assert [entry["name"] for entry in body] == ["Second", "First"]
