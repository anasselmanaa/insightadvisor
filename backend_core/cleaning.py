import pandas as pd
import numpy as np


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names consistent: lowercase, underscores, no spaces"""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "_", regex=True)
    )
    return df


def detect_column_types(df: pd.DataFrame) -> dict:
    """
    Auto-detect what each column represents.
    Returns dict: {col_name: 'numeric' | 'date' | 'categorical'}
    """
    types = {}
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            types[col] = "numeric"
        elif df[col].dtype == "object":
            # Try to parse as date
            sample = df[col].dropna().head(50)
            try:
                pd.to_datetime(sample, errors="raise", format="mixed")
                types[col] = "date"
            except Exception:
                types[col] = "categorical"
        else:
            types[col] = "other"
    return types


def remove_outliers_iqr(df: pd.DataFrame, col: str) -> tuple[pd.DataFrame, int]:
    """
    Remove outliers using IQR method.
    Keeps values within [Q1 - 1.5*IQR, Q3 + 1.5*IQR].
    Returns cleaned df + number of rows removed.
    """
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    if IQR == 0:
        return df, 0

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    before = len(df)
    df = df[(df[col] >= lower) & (df[col] <= upper)]
    removed = before - len(df)
    return df, removed


def calculate_quality_score(report: dict) -> int:
    """
    Calculate data quality score 0-100.
    Penalizes for: missing values, duplicates, outliers.
    """
    score = 100

    # Penalize for missing values (max -50 points)
    total_missing = sum(report.get("missing_before", {}).values())
    total_cells = report.get("rows_before", 1) * report.get("cols_before", 1)
    if total_cells > 0:
        missing_pct = total_missing / total_cells
        score -= int(missing_pct * 50)

    # Penalize for duplicates (max -30 points)
    rows_before = report.get("rows_before", 1)
    if rows_before > 0:
        dup_pct = report.get("duplicates_removed", 0) / rows_before
        score -= int(dup_pct * 30)

    # Penalize for outliers (max -20 points)
    total_outliers = sum(report.get("outliers_removed", {}).values())
    if rows_before > 0:
        out_pct = total_outliers / rows_before
        score -= int(out_pct * 20)

    return max(0, min(100, score))


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Full cleaning pipeline:
    1. Standardize column names
    2. Detect column types
    3. Remove duplicates
    4. Auto-convert date columns
    5. Fill missing values (smart strategy per column type)
    6. Remove outliers (IQR method) from numeric columns
    7. Create revenue column if quantity + price exist
    8. Calculate quality score
    """
    report = {}

    # 1) Standardize columns
    df = standardize_columns(df)

    report["rows_before"] = int(df.shape[0])
    report["cols_before"] = int(df.shape[1])
    report["columns"]     = list(df.columns)

    # 2) Detect column types
    col_types = detect_column_types(df)
    report["column_types"] = col_types

    # 3) Remove duplicates
    dup_count = int(df.duplicated().sum())
    df = df.drop_duplicates()
    report["duplicates_removed"] = dup_count

    # 4) Auto-convert date columns
    for col, ctype in col_types.items():
        if ctype == "date":
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 5) Handle missing values — smart strategy per column type
    missing_before = {k: int(v) for k, v in df.isna().sum().items()}
    fill_strategies = {}

    for col, ctype in col_types.items():
        if col not in df.columns:
            continue
        if ctype == "numeric":
            skewness = df[col].skew()
            if abs(skewness) > 1:
                fill_val = df[col].median()
                strategy = "median"
            else:
                fill_val = df[col].mean()
                strategy = "mean"
            df[col] = df[col].fillna(fill_val)
            fill_strategies[col] = strategy
        elif ctype == "categorical":
            df[col] = df[col].fillna("unknown")
            fill_strategies[col] = "unknown"
        elif ctype == "date":
            df[col] = df[col].ffill()
            fill_strategies[col] = "forward_fill"

    missing_after = {k: int(v) for k, v in df.isna().sum().items()}
    report["missing_before"]   = missing_before
    report["missing_after"]    = missing_after
    report["fill_strategies"]  = fill_strategies

    # 6) Remove outliers from numeric columns (IQR method)
    outliers_removed = {}
    for col, ctype in col_types.items():
        if ctype == "numeric" and col in df.columns:
            df, removed = remove_outliers_iqr(df, col)
            if removed > 0:
                outliers_removed[col] = removed
    report["outliers_removed"] = outliers_removed

    # 7) Create revenue column if quantity + price exist
    def _pick_col(df, candidates):
        cols = {c.lower().replace(" ","_"): c for c in df.columns}
        for cand in candidates:
            c = cand.lower().replace(" ","_")
            if c in cols:
                return cols[c]
            for k, v in cols.items():
                if c in k or k in c:
                    return v
        return None
    qty_col   = _pick_col(df, ["quantity","qty","stock_quantity","units","count","volume","stock"])
    price_col = _pick_col(df, ["price","unit_price","unitprice","selling_price","cost","amount","rate"])

    if qty_col and price_col:
        df["revenue"] = df[qty_col] * df[price_col]
        report["revenue_column_created"] = True
    else:
        report["revenue_column_created"] = False

    report["rows_after"] = int(df.shape[0])
    report["cols_after"] = int(df.shape[1])

    # 8) Calculate quality score
    report["quality_score"] = calculate_quality_score(report)

    return df, report