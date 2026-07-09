from fastapi.testclient import TestClient


def create_sample(
    client: TestClient,
    headers: dict[str, str],
) -> dict:
    response = client.post(
        "/samples",
        headers=headers,
        json={
            "sample_id": "LAB-QC-001",
            "test_type": "STI",
            "received_date": "2026-07-08T15:30:00",
            "status": "qc_review",
            "priority": "urgent",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_qc_note(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.post(
        f"/samples/{sample['id']}/qc-notes",
        headers=tech_headers,
        json={
            "note": "Control failed. Repeat testing required.",
            "note_type": "failed_control",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sample_db_id"] == sample["id"]
    assert data["note_type"] == "failed_control"
    assert data["created_by_id"] == 2


def test_list_qc_notes(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    client.post(
        f"/samples/{sample['id']}/qc-notes",
        headers=tech_headers,
        json={
            "note": "Missing patient-independent mock info.",
            "note_type": "missing_info",
        },
    )

    response = client.get(
        f"/samples/{sample['id']}/qc-notes",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["note_type"] == "missing_info"


def test_qc_note_creates_audit_log(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    client.post(
        f"/samples/{sample['id']}/qc-notes",
        headers=tech_headers,
        json={
            "note": "Repeat needed due to control issue.",
            "note_type": "repeat_needed",
        },
    )

    response = client.get(
        f"/audit-log/{sample['id']}",
        headers=tech_headers,
    )

    assert response.status_code == 200

    audit_logs = response.json()

    assert len(audit_logs) == 1
    assert audit_logs[0]["action"] == "qc_note_added"
    assert audit_logs[0]["field_name"] == "qc_notes"


def test_bad_qc_note_type_fails_validation(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    sample = create_sample(client, tech_headers)

    response = client.post(
        f"/samples/{sample['id']}/qc-notes",
        headers=tech_headers,
        json={
            "note": "Bad note type.",
            "note_type": "not_real",
        },
    )

    assert response.status_code == 422
