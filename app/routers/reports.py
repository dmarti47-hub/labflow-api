from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sample import Sample
from app.schemas.report import (
    OverdueSamplesReport,
    StatusSummaryReport,
    TestTypeSummaryReport,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/status-summary",
    response_model=StatusSummaryReport,
)
def get_status_summary(
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(
            Sample.status,
            func.count(Sample.id),
        )
        .where(Sample.is_deleted.is_(False))
        .group_by(Sample.status)
        .order_by(Sample.status)
    ).all()

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


@router.get(
    "/test-type-summary",
    response_model=TestTypeSummaryReport,
)
def get_test_type_summary(
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(
            Sample.test_type,
            func.count(Sample.id),
        )
        .where(Sample.is_deleted.is_(False))
        .group_by(Sample.test_type)
        .order_by(Sample.test_type)
    ).all()

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


@router.get(
    "/overdue",
    response_model=OverdueSamplesReport,
)
def get_overdue_samples(
    db: Session = Depends(get_db),
):
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

    samples = db.scalars(
        select(Sample)
        .where(
            Sample.is_deleted.is_(False),
            ~Sample.status.in_(["resulted", "cancelled"]),
            overdue_conditions,
        )
        .order_by(Sample.received_date.asc())
    ).all()

    return {
        "items": samples,
        "total": len(samples),
        "rules": {
            "urgent": "Overdue after 24 hours",
            "repeat": "Overdue after 48 hours",
            "routine": "Overdue after 72 hours",
        },
    }
