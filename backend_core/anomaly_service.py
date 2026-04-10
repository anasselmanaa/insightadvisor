import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _explain_anomaly(row: pd.Series, col_stats: dict) -> str:
    """
    Generate a plain English explanation for why a row is anomalous.
    Compares each numeric value to the column mean.
    """
    explanations = []

    for col, stats in col_stats.items():
        if col not in row.index:
            continue
        val  = row[col]
        mean = stats["mean"]
        std  = stats["std"]

        if std == 0:
            continue

        z_score = abs((val - mean) / std)

        if z_score > 3:
            direction = "higher" if val > mean else "lower"
            explanations.append(
                f"{col}={round(val, 2)} is {round(z_score, 1)}x "
                f"std {direction} than average ({round(mean, 2)})"
            )

    if explanations:
        return "Anomalous because: " + "; ".join(explanations[:3])
    return "Statistical outlier detected across multiple features"


def detect_anomalies(
    df:            pd.DataFrame,
    contamination: float = 0.05,
    top_n:         int   = 20,
) -> dict:
    """
    Full anomaly detection pipeline:
    1. Select numeric columns
    2. Scale features
    3. Fit Isolation Forest
    4. Score each row
    5. Flag top N most anomalous rows
    6. Generate plain English explanations
    7. Return results
    """
    df = _normalize_columns(df)

    # Step 1 — Select numeric columns
    # Exclude ID-like columns
    exclude = [c for c in df.columns if "id" in c or "date" in c or "invoice" in c]
    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns
        if c not in exclude
    ]

    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found for anomaly detection.")

    # Drop rows with any NaN in selected columns
    df_clean = df[numeric_cols].dropna()

    if len(df_clean) < 20:
        raise ValueError(
            f"Not enough rows for anomaly detection: {len(df_clean)}. Need at least 20."
        )

    # Step 2 — Scale
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean.values)

    # Step 3 — Fit Isolation Forest
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    predictions    = model.fit_predict(X_scaled)
    anomaly_scores = model.score_samples(X_scaled)

    # Step 4 — Add results back to dataframe
    df_result = df_clean.copy()
    df_result["is_anomaly"]    = predictions == -1
    df_result["anomaly_score"] = anomaly_scores
    df_result["row_index"]     = df_clean.index

    # Step 5 — Column statistics for explanation
    col_stats = {
        col: {
            "mean": float(df_clean[col].mean()),
            "std":  float(df_clean[col].std()),
        }
        for col in numeric_cols
    }

    # Step 6 — Get top N most anomalous rows
    anomalies = (
        df_result[df_result["is_anomaly"]]
        .sort_values("anomaly_score")
        .head(top_n)
    )

    anomaly_list = []
    for _, row in anomalies.iterrows():
        explanation = _explain_anomaly(row[numeric_cols], col_stats)

        anomaly_list.append({
            "row_index":     int(row["row_index"]),
            "anomaly_score": round(float(row["anomaly_score"]), 4),
            "values": {
                col: round(float(row[col]), 2)
                for col in numeric_cols
            },
            "explanation": explanation,
            "severity": (
                "High"   if row["anomaly_score"] < -0.775 else
                "Medium" if row["anomaly_score"] < -0.765 else
                "Low"
            )
        })

    # Step 7 — Summary statistics
    total_anomalies = int(df_result["is_anomaly"].sum())
    anomaly_pct     = round(total_anomalies / len(df_result) * 100, 2)

    return {
        "total_rows":       len(df_result),
        "total_anomalies":  total_anomalies,
        "anomaly_pct":      anomaly_pct,
        "contamination":    contamination,
        "features_used":    numeric_cols,
        "top_anomalies":    anomaly_list,
        "summary": {
            "high_severity":   sum(1 for a in anomaly_list if a["severity"] == "High"),
            "medium_severity": sum(1 for a in anomaly_list if a["severity"] == "Medium"),
            "low_severity":    sum(1 for a in anomaly_list if a["severity"] == "Low"),
        }
    }