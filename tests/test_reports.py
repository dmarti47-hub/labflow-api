from fastapi.testclient import TestClient


def create_sample(
    client: TestClient,
    headers: dict[str, str],
    sample_id: str,
    test_type: str,
    received_date: str,
    status: str,
    priority: str,
) -> dict:
    response = client.post(
        "/samples",
        headers=headers,
        json={
            "sample_id": sample_id,
            "test_type": test_type,
            "received_date": received_date,
            "status": status,
            "priority": priority,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_status_summary_report(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-REPORT-001",
        test_type="STI",
        received_date="2026-07-08T15:30:00",
        status="received",
        priority="routine",
    )

    create_sample(
        client,
        tech_headers,
        sample_id="LAB-REPORT-002",
        test_type="Respiratory Panel",
        received_date="2026-07-08T16:30:00",
        status="processing",
        priority="urgent",
    )

    response = client.get(
        "/reports/status-summary",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    totals_by_status = {
        item["status"]: item["total"]
        for item in data["items"]
    }

    assert totals_by_status["received"] == 1
    assert totals_by_status["processing"] == 1
    assert data["total"] == 2


def test_test_type_summary_report(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-REPORT-001",
        test_type="STI",
        received_date="2026-07-08T15:30:00",
        status="received",
        priority="routine",
    )

    create_sample(
        client,
        tech_headers,
        sample_id="LAB-REPORT-002",
        test_type="STI",
        received_date="2026-07-08T16:30:00",
        status="processing",
        priority="urgent",
    )

    response = client.get(
        "/reports/test-type-summary",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"][0]["test_type"] == "STI"
    assert data["items"][0]["total"] == 2
    assert data["total"] == 2


def test_overdue_report_includes_old_unresulted_samples(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-OVERDUE-001",
        test_type="STI",
        received_date="2026-07-01T08:00:00",
        status="processing",
        priority="urgent",
    )

    response = client.get(
        "/reports/overdue",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["sample_id"] == "LAB-OVERDUE-001"
    assert data["rules"]["urgent"] == "Overdue after 24 hours"


def test_overdue_report_excludes_resulted_samples(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-OVERDUE-RESULTED",
        test_type="STI",
        received_date="2026-07-01T08:00:00",
        status="resulted",
        priority="urgent",
    )

    response = client.get(
        "/reports/overdue",
        headers=tech_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0

def test_status_summary_csv_export(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-CSV-STATUS-001",
        test_type="STI",
        received_date="2026-07-08T15:30:00",
        status="received",
        priority="routine",
    )

    response = client.get(
        "/reports/status-summary/export",
        headers=tech_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "status-summary.csv" in response.headers["content-disposition"]
    assert "status,total" in response.text
    assert "received,1" in response.text


def test_test_type_summary_csv_export(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-CSV-TYPE-001",
        test_type="STI",
        received_date="2026-07-08T15:30:00",
        status="received",
        priority="routine",
    )

    response = client.get(
        "/reports/test-type-summary/export",
        headers=tech_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "test-type-summary.csv" in response.headers["content-disposition"]
    assert "test_type,total" in response.text
    assert "STI,1" in response.text


def test_overdue_csv_export(
    client: TestClient,
    tech_headers: dict[str, str],
) -> None:
    create_sample(
        client,
        tech_headers,
        sample_id="LAB-CSV-OVERDUE-001",
        test_type="STI",
        received_date="2026-07-01T08:00:00",
        status="processing",
        priority="urgent",
    )

    response = client.get(
        "/reports/overdue/export",
        headers=tech_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "overdue-samples.csv" in response.headers["content-disposition"]
    assert "sample_id,test_type,received_date,status,priority" in response.text
    assert "LAB-CSV-OVERDUE-001" in response.text


def test_csv_exports_require_auth(client: TestClient) -> None:
    response = client.get("/reports/status-summary/export")

    assert response.status_code == 401