from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.qc_note import QCNote
from app.models.sample import Sample
from app.models.user import User
from app.schemas.qc_note import QCNoteCreate, QCNoteOut


router = APIRouter(
    prefix="/samples/{sample_db_id}/qc-notes",
    tags=["QC Notes"],
)


def get_sample_or_error(db: Session, sample_db_id: int) -> Sample:
    sample = db.get(Sample, sample_db_id)

    if sample is None or sample.is_deleted:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sample not found.",
        )

    return sample


@router.post(
    "",
    response_model=QCNoteOut,
    status_code=http_status.HTTP_201_CREATED,
)
def create_qc_note(
    sample_db_id: int,
    payload: QCNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sample = get_sample_or_error(db=db, sample_db_id=sample_db_id)

    qc_note = QCNote(
        sample_db_id=sample.id,
        note=payload.note,
        note_type=payload.note_type,
        created_by_id=current_user.id,
    )

    db.add(qc_note)
    db.flush()

    db.add(
        AuditLog(
            sample_db_id=sample.id,
            changed_by_id=current_user.id,
            action="qc_note_added",
            field_name="qc_notes",
            old_value=None,
            new_value=f"{payload.note_type}: {payload.note}",
        )
    )

    db.commit()
    db.refresh(qc_note)

    return qc_note


@router.get(
    "",
    response_model=list[QCNoteOut],
)
def list_qc_notes(
    sample_db_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    get_sample_or_error(db=db, sample_db_id=sample_db_id)

    qc_notes = db.scalars(
        select(QCNote)
        .where(QCNote.sample_db_id == sample_db_id)
        .order_by(desc(QCNote.created_at))
    ).all()

    return qc_notes
