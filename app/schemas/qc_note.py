from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


QCNoteType = Literal[
    "failed_control",
    "repeat_needed",
    "missing_info",
    "instrument_issue",
    "general",
]


class QCNoteCreate(BaseModel):
    note: str = Field(
        min_length=3,
        max_length=2000,
        examples=["Control failed. Repeat testing required."],
    )
    note_type: QCNoteType = "general"

    @field_validator("note")
    @classmethod
    def strip_note(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Note cannot be blank.")
        return cleaned


class QCNoteOut(BaseModel):
    id: int
    sample_db_id: int
    note: str
    note_type: str
    created_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
