from fastapi.testclient import TestClient


def test_admin_can_list_users(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["email"] == "admin@example.com"
    assert data[1]["email"] == "tech@example.com"


def test_tech_cannot_list_users(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users",
        headers=tech_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required."


def test_admin_can_get_user(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users/2",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["email"] == "tech@example.com"


def test_get_missing_user_returns_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users/999",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_admin_can_update_user_role(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/2/role",
        headers=admin_headers,
        json={"role": "admin"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["role"] == "admin"


def test_invalid_role_fails_validation(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/2/role",
        headers=admin_headers,
        json={"role": "superuser"},
    )

    assert response.status_code == 422


def test_admin_can_deactivate_user(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/2/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["is_active"] is False


def test_admin_cannot_deactivate_self(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/1/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Admins cannot deactivate their own account."


def test_admin_can_activate_user(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    deactivate_response = client.patch(
        "/users/2/deactivate",
        headers=admin_headers,
    )

    assert deactivate_response.status_code == 200

    activate_response = client.patch(
        "/users/2/activate",
        headers=admin_headers,
    )

    assert activate_response.status_code == 200

    data = activate_response.json()

    assert data["id"] == 2
    assert data["is_active"] is True