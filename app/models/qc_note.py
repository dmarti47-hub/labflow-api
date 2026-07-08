from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QCNote(Base):
    __tablename__ = "qc_notes"

    __table_args__ = (
        CheckConstraint(
            "note_type IN ('failed_control', 'repeat_needed', 'missing_info', 'instrument_issue', 'general')",
            name="ck_qc_notes_note_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    sample_db_id: Mapped[int] = mapped_column(
        ForeignKey("samples.id"),
        nullable=False,
        index=True,
    )

    note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    note_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="general",
        server_default="general",
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sample = relationship(
        "Sample",
        back_populates="qc_notes",
    )

    creator = relationship(
        "User",
        back_populates="qc_notes",
    )
