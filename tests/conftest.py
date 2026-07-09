from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.security import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import AuditLog, QCNote, Sample, User  # noqa: F401


TEST_DATABASE_URL = (
    "postgresql+psycopg://labflow_user:labflow_password"
    "@localhost:5433/labflow_test_db"
)


test_engine = create_engine(TEST_DATABASE_URL, echo=False)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        admin = User(
            email="admin@example.com",
            full_name="Development Admin",
            hashed_password=get_password_hash("AdminPassword123!"),
            role="admin",
            is_active=True,
        )

        tech = User(
            email="tech@example.com",
            full_name="Development Tech",
            hashed_password=get_password_hash("StrongPassword123!"),
            role="tech",
            is_active=True,
        )

        db.add_all([admin, tech])
        db.commit()

    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def tech_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={
            "username": "tech@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "AdminPassword123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def tech_headers(tech_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tech_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
