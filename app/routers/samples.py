from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sample import Sample
from app.models.user import User
from app.schemas.sample import (
    PaginatedSamples,
    SampleCreate,
    SampleOut,
    SamplePriority,
    SampleStatus,
)


router = APIRouter(
    prefix="/samples",
    tags=["Samples"],
)


@router.post(
    "",
    response_model=SampleOut,
    status_code=http_status.HTTP_201_CREATED,
)
def create_sample(
    payload: SampleCreate,
    db: Session = Depends(get_db),
):
    creator = db.get(User, payload.created_by_id)

    if creator is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="created_by_id does not match an existing user.",
        )

    if payload.assigned_to_id is not None:
        assigned_user = db.get(User, payload.assigned_to_id)

        if assigned_user is None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="assigned_to_id does not match an existing user.",
            )

    sample = Sample(**payload.model_dump())

    db.add(sample)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A sample with this sample_id already exists.",
        ) from None

    db.refresh(sample)

    return sample


@router.get(
    "",
    response_model=PaginatedSamples,
)
def list_samples(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    status: SampleStatus | None = Query(default=None),
    test_type: str | None = Query(default=None, min_length=1, max_length=80),
    priority: SamplePriority | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    sort_by: Literal[
        "sample_id",
        "test_type",
        "received_date",
        "status",
        "priority",
        "created_at",
    ] = "received_date",
    sort_order: Literal["asc", "desc"] = "desc",
):
    conditions = [Sample.is_deleted.is_(False)]

    if status is not None:
        conditions.append(Sample.status == status)

    if test_type is not None:
        conditions.append(Sample.test_type.ilike(f"%{test_type.strip()}%"))

    if priority is not None:
        conditions.append(Sample.priority == priority)

    if start_date is not None:
        conditions.append(Sample.received_date >= start_date)

    if end_date is not None:
        conditions.append(Sample.received_date <= end_date)

    total = db.scalar(select(func.count()).select_from(Sample).where(*conditions))

    sort_columns = {
        "sample_id": Sample.sample_id,
        "test_type": Sample.test_type,
        "received_date": Sample.received_date,
        "status": Sample.status,
        "priority": Sample.priority,
        "created_at": Sample.created_at,
    }

    sort_column = sort_columns[sort_by]
    order_clause = desc(sort_column) if sort_order == "desc" else asc(sort_column)

    offset = (page - 1) * page_size

    samples = db.scalars(
        select(Sample)
        .where(*conditions)
        .order_by(order_clause)
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "items": samples,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/{sample_db_id}",
    response_model=SampleOut,
)
def get_sample(
    sample_db_id: int,
    db: Session = Depends(get_db),
):
    sample = db.get(Sample, sample_db_id)

    if sample is None or sample.is_deleted:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sample not found.",
        )

    return sample
