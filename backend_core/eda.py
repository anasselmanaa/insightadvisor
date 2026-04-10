import pandas as pd
import numpy as np


def generate_eda_report(df: pd.DataFrame) -> dict:
    """
    Full EDA pipeline:
    1. Basic overview (shape, columns, dtypes)
    2. Missing values summary
    3. Numeric column statistics
    4. Categorical column summaries
    5. Correlation matrix
    6. Distribution summary per numeric column
    7. Top categories per categorical column
    8. Date range detection
    9. Outlier count per numeric column
    """
    report = {}

    # 1) Basic overview
    report["shape"]   = list(df.shape)
    report["columns"] = list(df.columns)
    report["dtypes"]  = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # 2) Missing values
    report["missing"] = {
        k: int(v) for k, v in df.isna().sum().items()
    }
    report["missing_pct"] = {
        k: round(float(v) / len(df) * 100, 2) if len(df) > 0 else 0.0
        for k, v in df.isna().sum().items()
    }

    # 3) Numeric summary
    numeric_cols = df.select_dtypes(include="number")
    if not numeric_cols.empty:
        report["numeric_summary"] = (
            numeric_cols.describe()
            .round(2)
            .to_dict()
        )
    else:
        report["numeric_summary"] = {}

    # 4) Categorical summary
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    report["categorical_summary"] = {
        col: {
            "unique_count": int(df[col].nunique()),
            "top_10": df[col].value_counts().head(10).to_dict()
        }
        for col in categorical_cols
    }

    # 5) Correlation matrix
    if not numeric_cols.empty and numeric_cols.shape[1] >= 2:
        corr = numeric_cols.corr().round(3)
        # Replace NaN with None for clean JSON
        report["correlation_matrix"] = {
            col: {
                k: (None if pd.isna(v) else float(v))
                for k, v in row.items()
            }
            for col, row in corr.to_dict().items()
        }
    else:
        report["correlation_matrix"] = {}

    # 6) Distribution summary per numeric column
    report["distributions"] = {}
    for col in numeric_cols.columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        report["distributions"][col] = {
            "min":    round(float(series.min()), 2),
            "max":    round(float(series.max()), 2),
            "mean":   round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "std":    round(float(series.std()), 2),
            "skew":   round(float(series.skew()), 2),
            "q25":    round(float(series.quantile(0.25)), 2),
            "q75":    round(float(series.quantile(0.75)), 2),
        }

    # 7) Top categories per categorical column
    report["top_categories"] = {}
    for col in categorical_cols:
        top = df[col].value_counts().head(5)
        report["top_categories"][col] = {
            "values": top.index.tolist(),
            "counts": [int(x) for x in top.values.tolist()],
        }

    # 8) Date range detection
    report["date_ranges"] = {}
    date_cols = [
        col for col in df.columns
        if pd.api.types.is_datetime64_any_dtype(df[col])
    ]
    for col in date_cols:
        series = df[col].dropna()
        if len(series) > 0:
            report["date_ranges"][col] = {
                "min": str(series.min().date()),
                "max": str(series.max().date()),
                "days_span": int((series.max() - series.min()).days),
            }

    # 9) Outlier count per numeric column (IQR method)
    report["outlier_counts"] = {}
    for col in numeric_cols.columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        Q1  = series.quantile(0.25)
        Q3  = series.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        outliers = series[
            (series < Q1 - 1.5 * IQR) |
            (series > Q3 + 1.5 * IQR)
        ]
        if len(outliers) > 0:
            report["outlier_counts"][col] = int(len(outliers))

    return report