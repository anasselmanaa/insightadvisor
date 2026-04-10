from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import json

from backend_core.storage import cleaned_path, arima_report_path
from backend_core.arima_service import run_arima_forecast

router = APIRouter(tags=["ARIMA"])


@router.get("/arima/{dataset_id}")
def run_arima(
    dataset_id: str,
    forecast_days: int = Query(default=30, ge=7,  le=365),
    p:            int = Query(default=1,  ge=0,  le=5),
    d:            int = Query(default=1,  ge=0,  le=2),
    q:            int = Query(default=1,  ge=0,  le=5),
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

    # 3) Run ARIMA
    try:
        result = run_arima_forecast(
            df,
            forecast_days=forecast_days,
            p=p, d=d, q=q
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ARIMA failed: {str(e)}"
        )

    # 4) Save report
    out = arima_report_path(dataset_id)
    out.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status":       "success",
        "dataset_id":   dataset_id,
        "arima":        result,
        "saved_report": str(out)
    }