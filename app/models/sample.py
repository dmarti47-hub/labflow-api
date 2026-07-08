from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sample(Base):
    __tablename__ = "samples"

    __table_args__ = (
        CheckConstraint(
            "status IN ('received', 'processing', 'qc_review', 'resulted', 'cancelled')",
            name="ck_samples_status",
        ),
        CheckConstraint(
            "priority IN ('routine', 'urgent', 'repeat')",
            name="ck_samples_priority",
        ),
        Index("ix_samples_status_test_type", "status", "test_type"),
        Index("ix_samples_received_date", "received_date"),
        Index("ix_samples_is_deleted", "is_deleted"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    sample_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    test_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    received_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="received",
        server_default="received",
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="routine",
        server_default="routine",
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    assigned_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    creator = relationship(
        "User",
        back_populates="created_samples",
        foreign_keys=[created_by_id],
    )

    assigned_user = relationship(
        "User",
        back_populates="assigned_samples",
        foreign_keys=[assigned_to_id],
    )

    qc_notes = relationship(
        "QCNote",
        back_populates="sample",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="sample",
        cascade="all, delete-orphan",
    )
