from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import json
import io

from backend_core.storage import (
    ensure_dirs,
    new_dataset_id,
    upload_path,
    cleaned_path,
    cleaning_report_path,
)
from backend_core.cleaning import clean_dataframe

router = APIRouter(tags=["Upload"])

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _read_file(content: bytes, filename: str) -> pd.DataFrame:
    """Read CSV or Excel file into DataFrame"""
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(io.BytesIO(content))
    elif ext in {".xlsx", ".xls"}:
        return pd.read_excel(io.BytesIO(content))
    raise ValueError(f"Unsupported file type: {ext}")


def _detect_dataset_type(df: pd.DataFrame) -> str:
    """
    Auto-detect whether this is retail, stock, or generic data.
    Returns: 'retail', 'stock', or 'generic'
    """
    cols = set(df.columns.str.lower().str.replace(" ", "_"))

    # Stock market signals
    stock_signals = {"open", "close", "high", "low", "volume", "adj_close"}
    if len(stock_signals & cols) >= 3:
        return "stock"

    # Retail signals
    retail_signals = {"invoice", "quantity", "price", "customer_id",
                      "customerid", "stockcode", "description"}
    if len(retail_signals & cols) >= 3:
        return "retail"

    return "generic"


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    ensure_dirs()

    # 1) Validate file extension
    filename = file.filename or "upload.csv"
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {SUPPORTED_EXTENSIONS}"
        )

    # 2) Read content
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 3) File size check (max 200MB)
    size_mb = len(content) / (1024 * 1024)
    if size_mb > 200:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Maximum is 200MB."
        )

    # 4) Create dataset ID + save raw file
    dataset_id = new_dataset_id()
    raw_file_path = upload_path(dataset_id, filename)
    raw_file_path.write_bytes(content)

    # 5) Read into DataFrame
    try:
        df = _read_file(content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="File has no data rows.")

    # 6) Detect dataset type (retail / stock / generic)
    dataset_type = _detect_dataset_type(df)

    # 7) Auto-trigger cleaning
    try:
        cleaned_df, report = clean_dataframe(df)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cleaning failed: {str(e)}"
        )

    # 8) Add dataset type to report
    report["dataset_type"] = dataset_type

    # 9) Save cleaned CSV + report
    cleaned_file_path = cleaned_path(dataset_id)
    cleaned_df.to_csv(cleaned_file_path, index=False)

    report_file_path = cleaning_report_path(dataset_id)
    report_file_path.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status": "success",
        "dataset_id": dataset_id,
        "dataset_type": dataset_type,
        "raw_rows": int(df.shape[0]),
        "raw_cols": int(df.shape[1]),
        "cleaned_rows": int(cleaned_df.shape[0]),
        "cleaned_cols": int(cleaned_df.shape[1]),
        "quality_score": report.get("quality_score", 0),
        "duplicates_removed": report.get("duplicates_removed", 0),
        "outliers_removed": report.get("outliers_removed", {}),
        "missing_before": report.get("missing_before", {}),
        "files": {
            "raw": str(raw_file_path),
            "cleaned": str(cleaned_file_path),
            "cleaning_report": str(report_file_path),
        }
    }