from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend_core.database import get_db
from backend_core.audit_service import log_action, get_audit_log

router = APIRouter(tags=["Audit"])


@router.get("/audit/{dataset_id}")
def audit_log(dataset_id: str, db: Session = Depends(get_db)):
    try:
        logs = get_audit_log(db, dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log: {str(e)}")
    return {
        "status":     "success",
        "dataset_id": dataset_id,
        "total":      len(logs),
        "log":        logs,
    }


@router.post("/audit/{dataset_id}/log")
def manual_log(
    dataset_id: str,
    action: str,
    details: str = "",
    db: Session = Depends(get_db),
):
    log_action(db, dataset_id, action, details)
    return {"status": "success", "message": "Action logged"}
