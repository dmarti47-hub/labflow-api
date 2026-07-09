import csv
from io import StringIO

from fastapi import APIRouter, Depends, Response
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.sample import Sample
from app.models.user import User
from app.schemas.report import (
    OverdueSamplesReport,
    StatusSummaryReport,
    TestTypeSummaryReport,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def build_csv_response(
    filename: str,
    headers: list[str],
    rows: list[list[object]],
) -> Response:
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)
    writer.writerows(rows)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


def get_status_summary_rows(db: Session) -> list[tuple[str, int]]:
    return db.execute(
        select(
            Sample.status,
            func.count(Sample.id),
        )
        .where(Sample.is_deleted.is_(False))
        .group_by(Sample.status)
        .order_by(Sample.status)
    ).all()


def get_test_type_summary_rows(db: Session) -> list[tuple[str, int]]:
    return db.execute(
        select(
            Sample.test_type,
            func.count(Sample.id),
        )
        .where(Sample.is_deleted.is_(False))
        .group_by(Sample.test_type)
        .order_by(Sample.test_type)
    ).all()


def get_overdue_sample_rows(db: Session) -> list[Sample]:
    overdue_conditions = or_(
        and_(
            Sample.priority == "urgent",
            Sample.received_date <= func.now() - text("interval '24 hours'"),
        ),
        and_(
            Sample.priority == "repeat",
            Sample.received_date <= func.now() - text("interval '48 hours'"),
        ),
        and_(
            Sample.priority == "routine",
            Sample.received_date <= func.now() - text("interval '72 hours'"),
        ),
    )

    return db.scalars(
        select(Sample)
        .where(
            Sample.is_deleted.is_(False),
            ~Sample.status.in_(["resulted", "cancelled"]),
            overdue_conditions,
        )
        .order_by(Sample.received_date.asc())
    ).all()


@router.get(
    "/status-summary",
    response_model=StatusSummaryReport,
)
def get_status_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    rows = get_status_summary_rows(db)

    items = [
        {
            "status": status,
            "total": total,
        }
        for status, total in rows
    ]

    return {
        "items": items,
        "total": sum(item["total"] for item in items),
    }


@router.get("/status-summary/export")
def export_status_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    rows = get_status_summary_rows(db)

    csv_rows = [
        [status, total]
        for status, total in rows
    ]

    return build_csv_response(
        filename="status-summary.csv",
        headers=["status", "total"],
        rows=csv_rows,
    )


@router.get(
    "/test-type-summary",
    response_model=TestTypeSummaryReport,
)
def get_test_type_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    rows = get_test_type_summary_rows(db)

    items = [
        {
            "test_type": test_type,
            "total": total,
        }
        for test_type, total in rows
    ]

    return {
        "items": items,
        "total": sum(item["total"] for item in items),
    }


@router.get("/test-type-summary/export")
def export_test_type_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    rows = get_test_type_summary_rows(db)

    csv_rows = [
        [test_type, total]
        for test_type, total in rows
    ]

    return build_csv_response(
        filename="test-type-summary.csv",
        headers=["test_type", "total"],
        rows=csv_rows,
    )


@router.get(
    "/overdue",
    response_model=OverdueSamplesReport,
)
def get_overdue_samples(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    samples = get_overdue_sample_rows(db)

    return {
        "items": samples,
        "total": len(samples),
        "rules": {
            "urgent": "Overdue after 24 hours",
            "repeat": "Overdue after 48 hours",
            "routine": "Overdue after 72 hours",
        },
    }


@router.get("/overdue/export")
def export_overdue_samples(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    samples = get_overdue_sample_rows(db)

    csv_rows = [
        [
            sample.id,
            sample.sample_id,
            sample.test_type,
            sample.received_date.isoformat(),
            sample.status,
            sample.priority,
            sample.created_by_id,
            sample.assigned_to_id,
            sample.created_at.isoformat(),
            sample.updated_at.isoformat(),
        ]
        for sample in samples
    ]

    return build_csv_response(
        filename="overdue-samples.csv",
        headers=[
            "id",
            "sample_id",
            "test_type",
            "received_date",
            "status",
            "priority",
            "created_by_id",
            "assigned_to_id",
            "created_at",
            "updated_at",
        ],
        rows=csv_rows,
    )