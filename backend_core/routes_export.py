from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import json

from backend_core.storage import (
    ensure_dirs,
    cleaned_path,
    eda_report_path,
    kmeans_report_path,
    export_cleaned_excel_path,
    export_kmeans_excel_path,
    export_eda_json_path,
)

router = APIRouter(tags=["Export"])


@router.get("/export/cleaned/{dataset_id}")
def export_cleaned_excel(dataset_id: str):
    ensure_dirs()

    source_file = cleaned_path(dataset_id)
    if not source_file.exists():
        raise HTTPException(status_code=404, detail="Cleaned dataset not found.")

    try:
        df = pd.read_csv(source_file)
        output_file = export_cleaned_excel_path(dataset_id)
        df.to_excel(output_file, index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export cleaned dataset: {str(e)}")

    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/export/eda/{dataset_id}")
def export_eda_json(dataset_id: str):
    ensure_dirs()

    source_file = eda_report_path(dataset_id)
    if not source_file.exists():
        raise HTTPException(status_code=404, detail="EDA report not found.")

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            report = json.load(f)

        output_file = export_eda_json_path(dataset_id)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export EDA report: {str(e)}")

    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/json"
    )


@router.get("/export/kmeans/{dataset_id}")
def export_kmeans_excel(dataset_id: str):
    ensure_dirs()

    source_file = kmeans_report_path(dataset_id)
    if not source_file.exists():
        raise HTTPException(status_code=404, detail="KMeans report not found.")

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            report = json.load(f)

        customer_clusters = report.get("customer_clusters", [])
        cluster_profiles = report.get("cluster_profiles", [])

        customers_df = pd.DataFrame(customer_clusters)
        profiles_df = pd.DataFrame(cluster_profiles)

        output_file = export_kmeans_excel_path(dataset_id)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            customers_df.to_excel(writer, sheet_name="customer_clusters", index=False)
            profiles_df.to_excel(writer, sheet_name="cluster_profiles", index=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export KMeans results: {str(e)}")

    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@router.get("/export/pdf/{dataset_id}")
def export_pdf(dataset_id: str):
    ensure_dirs()
    from backend_core.pdf_service import generate_pdf
    try:
        output_file = generate_pdf(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/pdf"
    )

@router.get("/export/pptx/{dataset_id}")
def export_pptx(dataset_id: str):
    ensure_dirs()
    from backend_core.pptx_service import generate_pptx
    try:
        output_file = generate_pptx(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPTX generation failed: {str(e)}")
    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
