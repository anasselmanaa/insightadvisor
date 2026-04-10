from pathlib import Path
import uuid

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR     = BASE_DIR / "data"
UPLOAD_DIR   = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR   = DATA_DIR / "exports"
DB_PATH      = BASE_DIR / "retailiq.db"


def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def new_dataset_id() -> str:
    return uuid.uuid4().hex[:12]


# ── Upload ────────────────────────────────────────────
def upload_path(dataset_id: str, filename: str) -> Path:
    safe_name = filename.replace("/", "_").replace("\\", "_")
    return UPLOAD_DIR / f"{dataset_id}__{safe_name}"


# ── Processed ─────────────────────────────────────────
def cleaned_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__cleaned.csv"

def cleaning_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__cleaning_report.json"

def eda_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__eda_report.json"

def kmeans_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__kmeans_report.json"

def arima_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__arima_report.json"

def apriori_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__apriori_report.json"

def regression_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__regression_report.json"

def anomaly_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__anomaly_report.json"

def ai_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__ai_report.json"

def stock_report_path(ticker: str) -> Path:
    return PROCESSED_DIR / f"stock__{ticker}__report.json"

def causal_report_path(dataset_id: str) -> Path:
    return PROCESSED_DIR / f"{dataset_id}__causal_report.json"


# ── Exports ───────────────────────────────────────────
def export_cleaned_excel_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__cleaned.xlsx"

def export_kmeans_excel_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__kmeans.xlsx"

def export_eda_json_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__eda_export.json"

def export_pdf_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__report.pdf"

def export_pptx_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__report.pptx"

def export_arima_excel_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__arima.xlsx"

def export_apriori_excel_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__apriori.xlsx"

def export_regression_excel_path(dataset_id: str) -> Path:
    return EXPORT_DIR / f"{dataset_id}__regression.xlsx"