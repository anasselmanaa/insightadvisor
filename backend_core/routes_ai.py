from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import json

from backend_core.storage import cleaned_path, ai_report_path
from backend_core.causal_service import run_causal_analysis
from backend_core.ai_service import (
    build_analysis_context,
    generate_recommendations,
    generate_action_plan,
    process_nl_query,
)

router = APIRouter(tags=["AI Copilot"])


# ── /causal/{dataset_id} ──────────────────────────────────────────
@router.get("/causal/{dataset_id}")
def causal_analysis(dataset_id: str):
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")

    try:
        df = pd.read_csv(cleaned_file)
        result = run_causal_analysis(df)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Causal analysis failed: {str(e)}")

    out = ai_report_path(dataset_id).parent / f"{dataset_id}__causal_report.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    return {"status": "success", "dataset_id": dataset_id, "causal": result}


# ── /ai/recommendations/{dataset_id} ─────────────────────────────
@router.get("/ai/recommendations/{dataset_id}")
def ai_recommendations(dataset_id: str):
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")

    try:
        reports_dir = ai_report_path(dataset_id).parent
        context     = build_analysis_context(reports_dir, dataset_id)
        result      = generate_recommendations(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

    out = ai_report_path(dataset_id)
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    return {"status": "success", "dataset_id": dataset_id, "ai": result}


# ── /ai/action-plan/{dataset_id} ─────────────────────────────────
@router.get("/ai/action-plan/{dataset_id}")
def ai_action_plan(dataset_id: str):
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")

    try:
        reports_dir = ai_report_path(dataset_id).parent
        context     = build_analysis_context(reports_dir, dataset_id)
        result      = generate_action_plan(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action plan failed: {str(e)}")

    return {"status": "success", "dataset_id": dataset_id, "action_plan": result}


# ── /ai/query/{dataset_id} ───────────────────────────────────────
class NLQueryRequest(BaseModel):
    query: str


@router.post("/ai/query/{dataset_id}")
def nl_query(dataset_id: str, body: NLQueryRequest):
    cleaned_file = cleaned_path(dataset_id)
    if not cleaned_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found. Upload first.")

    try:
        result = process_nl_query(dataset_id, body.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NL query failed: {str(e)}")

    return {"status": "success", "dataset_id": dataset_id, "result": result}