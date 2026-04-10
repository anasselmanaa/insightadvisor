from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import json

from backend_core.storage import cleaned_path, anomaly_report_path
from backend_core.anomaly_service import detect_anomalies

router = APIRouter(tags=["Anomaly"])


@router.get("/anomaly/{dataset_id}")
def run_anomaly_detection(
    dataset_id:    str,
    contamination: float = Query(default=0.05, ge=0.01, le=0.5),
    top_n:         int   = Query(default=20,   ge=5,    le=100),
):
    # 1) Find cleaned file
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Cleaned dataset not found. Upload first."
        )

    # 2) Load data
    try:
        df = pd.read_csv(cleaned_file)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read cleaned CSV: {str(e)}"
        )

    # 3) Run anomaly detection
    try:
        result = detect_anomalies(
            df,
            contamination=contamination,
            top_n=top_n
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(e)}"
        )

    # 4) Save report
    out = anomaly_report_path(dataset_id)
    out.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status":       "success",
        "dataset_id":   dataset_id,
        "anomaly":      result,
        "saved_report": str(out)
    }