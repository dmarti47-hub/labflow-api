from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": "tech@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure_with_wrong_password(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": "tech@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_auth_me_requires_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    response = client.get(
        "/auth/me",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "tech@example.com"
    assert data["role"] == "tech"


def test_register_new_user_defaults_to_tech(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "newtech@example.com",
            "full_name": "New Tech",
            "password": "AnotherStrongPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "newtech@example.com"
    assert data["role"] == "tech"
    assert "hashed_password" not in data
