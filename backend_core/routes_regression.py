from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import json

from backend_core.storage import cleaned_path, regression_report_path
from backend_core.regression_service import run_linear_regression

router = APIRouter(tags=["Regression"])


@router.get("/regression/{dataset_id}")
def run_regression(
    dataset_id: str,
    target_col: str = Query(
        default=None,
        description="Target column to predict. Leave empty for auto-detection."
    ),
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

    # 3) Run regression
    try:
        result = run_linear_regression(df, target_col=target_col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Regression failed: {str(e)}"
        )

    # 4) Save report
    out = regression_report_path(dataset_id)
    out.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status":       "success",
        "dataset_id":   dataset_id,
        "regression":   result,
        "saved_report": str(out)
    }