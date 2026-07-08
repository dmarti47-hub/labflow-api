from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SampleStatus = Literal[
    "received",
    "processing",
    "qc_review",
    "resulted",
    "cancelled",
]

SamplePriority = Literal[
    "routine",
    "urgent",
    "repeat",
]


class SampleBase(BaseModel):
    sample_id: str = Field(
        min_length=3,
        max_length=50,
        examples=["LAB-2026-001"],
    )
    test_type: str = Field(
        min_length=2,
        max_length=80,
        examples=["STI"],
    )
    received_date: datetime
    status: SampleStatus = "received"
    priority: SamplePriority = "routine"
    assigned_to_id: int | None = None

    @field_validator("sample_id", "test_type")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank.")
        return cleaned


class SampleCreate(SampleBase):
    created_by_id: int = Field(gt=0)


class SampleOut(BaseModel):
    id: int
    sample_id: str
    test_type: str
    received_date: datetime
    status: str
    priority: str
    created_by_id: int
    assigned_to_id: int | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedSamples(BaseModel):
    items: list[SampleOut]
    total: int
    page: int
    page_size: int
