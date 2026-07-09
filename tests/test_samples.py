from fastapi.testclient import TestClient


def create_sample(
    client: TestClient,
    headers: dict[str, str],
    sample_id: str = "LAB-TEST-001",
) -> dict:
    response = client.post(
        "/samples",
        headers=headers,
        json={
            "sample_id": sample_id,
            "test_type": "STI",
            "received_date": "2026-07-08T15:30:00",
            "status": "received",
            "priority": "routine",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_sample_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/samples",
        json={
            "sample_id": "LAB-TEST-001",
            "test_type": "STI",
            "received_date": "2026-07-08T15:30:00",
            "status": "received",
            "priority": "routine",
        },
    )

    assert response.status_code == 401


def test_create_sample_as_tech(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    assert sample["sample_id"] == "LAB-TEST-001"
    assert sample["test_type"] == "STI"
    assert sample["status"] == "received"
    assert sample["priority"] == "routine"
    assert sample["created_by_id"] == 2


def test_list_samples_with_pagination(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(client, tech_headers, sample_id="LAB-TEST-001")
    create_sample(client, tech_headers, sample_id="LAB-TEST-002")

    response = client.get(
        "/samples?page=1&page_size=10",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 2


def test_filter_samples_by_status(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    client.patch(
        f"/samples/{sample['id']}",
        headers=tech_headers,
        json={"status": "processing"},
    )

    response = client.get(
        "/samples?status=processing",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["status"] == "processing"


def test_get_sample_by_id(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.get(
        f"/samples/{sample['id']}",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sample["id"]
    assert data["sample_id"] == "LAB-TEST-001"


def test_duplicate_sample_id_returns_conflict(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(client, tech_headers, sample_id="LAB-DUPLICATE")

    response = client.post(
        "/samples",
        headers=tech_headers,
        json={
            "sample_id": "LAB-DUPLICATE",
            "test_type": "STI",
            "received_date": "2026-07-08T15:30:00",
            "status": "received",
            "priority": "routine",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "A sample with this sample_id already exists."


def test_update_sample_creates_audit_log(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.patch(
        f"/samples/{sample['id']}",
        headers=tech_headers,
        json={
            "status": "processing",
            "priority": "urgent",
        },
    )

    assert response.status_code == 200

    updated_sample = response.json()

    assert updated_sample["status"] == "processing"
    assert updated_sample["priority"] == "urgent"

    audit_response = client.get(
        f"/audit-log/{sample['id']}",
        headers=tech_headers,
    )

    assert audit_response.status_code == 200

    audit_logs = audit_response.json()

    changed_fields = {log["field_name"] for log in audit_logs}

    assert "status" in changed_fields
    assert "priority" in changed_fields


def test_tech_cannot_delete_sample(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.delete(
        f"/samples/{sample['id']}",
        headers=tech_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required."


def test_admin_can_soft_delete_sample(
    client: TestClient,
    tech_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.delete(
        f"/samples/{sample['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    deleted_sample = response.json()

    assert deleted_sample["is_deleted"] is True

    get_response = client.get(
        f"/samples/{sample['id']}",
        headers=tech_headers,
    )

    assert get_response.status_code == 404
