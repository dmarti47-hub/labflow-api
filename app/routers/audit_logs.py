from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.sample import Sample
from app.models.user import User
from app.schemas.audit_log import AuditLogOut


router = APIRouter(
    prefix="/audit-log",
    tags=["Audit Log"],
)


@router.get(
    "/{sample_db_id}",
    response_model=list[AuditLogOut],
)
def get_sample_audit_log(
    sample_db_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    sample = db.get(Sample, sample_db_id)

    if sample is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sample not found.",
        )

    audit_logs = db.scalars(
        select(AuditLog)
        .where(AuditLog.sample_db_id == sample_db_id)
        .order_by(desc(AuditLog.created_at))
    ).all()

    return audit_logs
