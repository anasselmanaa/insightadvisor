from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import json

from backend_core.storage import cleaned_path, apriori_report_path
from backend_core.apriori_service import run_apriori_auto as run_apriori

router = APIRouter(tags=["Apriori"])


@router.get("/apriori/{dataset_id}")
def run_apriori_endpoint(
    dataset_id:     str,
    min_support:    float = Query(default=0.01,  ge=0.001, le=0.5),
    min_confidence: float = Query(default=0.1,   ge=0.01,  le=1.0),
    max_rules:      int   = Query(default=20,    ge=5,     le=50),
    top_n_products: int   = Query(default=100,   ge=10,    le=500),
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

    # 3) Run Apriori
    try:
        result = run_apriori(
            df,
            min_support=min_support,
            min_confidence=min_confidence,
            max_rules=max_rules,
            top_n_products=top_n_products,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=(
            "This dataset does not contain transaction data required for "
            "association rule mining. Apriori works best with retail/sales "
            "datasets that have invoices and product descriptions. "
            f"Details: {str(e)}"
        ))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Apriori failed: {str(e)}"
        )

    # 4) Save report
    out = apriori_report_path(dataset_id)
    out.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status":       "success",
        "dataset_id":   dataset_id,
        "apriori":      result,
        "saved_report": str(out)
    }