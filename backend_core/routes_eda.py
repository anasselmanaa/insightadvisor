from fastapi import APIRouter, HTTPException
import pandas as pd
import json

from backend_core.storage import cleaned_path, eda_report_path


from backend_core.eda import generate_eda_report  


router = APIRouter(tags=["EDA"])


@router.get("/eda/{dataset_id}")
def run_eda(dataset_id: str):
    # 1) Find cleaned file
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")

    # 2) Load cleaned df
    try:
        df = pd.read_csv(cleaned_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read cleaned CSV: {str(e)}")

    # 3) Run EDA
    try:
        report = generate_eda_report(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EDA failed: {str(e)}")

    # 4) Save report JSON
    out = eda_report_path(dataset_id)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "dataset_id": dataset_id,
        "eda": report,
        "saved_report": str(out)
    }