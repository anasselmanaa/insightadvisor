from sqlalchemy.orm import Session
from backend_core.models import AuditLog


def log_action(db: Session, dataset_id: str, action: str, details: str = ""):
    try:
        entry = AuditLog(
            dataset_id=dataset_id,
            action=action,
            details=details,
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()


def get_audit_log(db: Session, dataset_id: str) -> list:
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.dataset_id == dataset_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return [
        {
            "id":         row.id,
            "dataset_id": row.dataset_id,
            "action":     row.action,
            "details":    row.details,
            "created_at": str(row.created_at),
        }
        for row in rows
    ]
