def test_submit_contact_success(client):
    response = client.post(
        "/api/contact",
        json={"name": "Jane Doe", "email": "jane@example.com", "message": "Hello!"},
    )
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_submit_contact_invalid_email(client):
    response = client.post(
        "/api/contact",
        json={"name": "Jane Doe", "email": "not-an-email", "message": "Hello!"},
    )
    assert response.status_code == 422


def test_submit_contact_missing_message(client):
    response = client.post(
        "/api/contact",
        json={"name": "Jane Doe", "email": "jane@example.com"},
    )
    assert response.status_code == 422


def test_submit_contact_blank_name_rejected(client):
    response = client.post(
        "/api/contact",
        json={"name": "", "email": "jane@example.com", "message": "Hello!"},
    )
    assert response.status_code == 422


def test_honeypot_submission_looks_like_success(client):
    # A filled-in honeypot field means a bot submitted it — the response
    # still looks like a normal success so the bot doesn't learn it was
    # caught (see test_admin.py for confirming it wasn't actually stored).
    response = client.post(
        "/api/contact",
        json={
            "name": "Spam Bot",
            "email": "bot@example.com",
            "message": "buy my stuff",
            "bot-field": "filled-in",
        },
    )
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
