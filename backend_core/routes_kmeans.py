import json
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from backend_core.storage import cleaned_path, kmeans_report_path
from backend_core.kmeans_service import run_kmeans_auto

router = APIRouter(tags=["KMeans"])

@router.get("/kmeans/{dataset_id}")
def kmeans(dataset_id: str, k: int = Query(4, ge=2, le=10)):
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")
    try:
        df = pd.read_csv(cleaned_file)
        result = run_kmeans_auto(df, k=k)
        report_file = kmeans_report_path(dataset_id)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KMeans failed: {str(e)}")
    return {"status": "success", "dataset_id": dataset_id, "result": result}
