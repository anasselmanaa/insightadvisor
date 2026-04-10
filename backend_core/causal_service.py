import json
import warnings
import numpy as np
import pandas as pd
from itertools import combinations

warnings.filterwarnings("ignore")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def _pick_column(df: pd.DataFrame, candidates: list) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _interpret_relationship(col_a: str, col_b: str, corr: float, pct_change: float) -> str:
    direction = "increase" if pct_change > 0 else "decrease"
    magnitude = round(abs(pct_change), 1)
    strength = "strongly" if abs(corr) > 0.6 else "moderately"

    a_label = col_a.replace("_", " ").title()
    b_label = col_b.replace("_", " ").title()

    return (
        f"{a_label} {strength} influences {b_label}. "
        f"A 10% change in {a_label} is associated with a {magnitude}% {direction} in {b_label}."
    )


def run_causal_analysis(df: pd.DataFrame) -> dict:
    """
    Perform statistical causal analysis using correlation + regression slopes.
    Returns plain-English relationships between numeric columns.
    No DoWhy dependency — uses scipy + numpy for reliable results.
    """
    df = _normalize_columns(df)

    # Step 1 — Prepare revenue column
    quantity_col = _pick_column(df, ["quantity"])
    price_col    = _pick_column(df, ["price", "unitprice", "unit_price"])
    revenue_col  = _pick_column(df, ["revenue", "sales", "total_sales"])

    if not revenue_col and quantity_col and price_col:
        df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
        df[price_col]    = pd.to_numeric(df[price_col], errors="coerce")
        df["revenue"]    = df[quantity_col] * df[price_col]

    # Step 2 — Select numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if df[c].notna().sum() > 30]

    if len(numeric_cols) < 2:
        return {
            "status": "error",
            "error": "Not enough numeric columns for causal analysis. Need at least 2.",
            "relationships": [],
            "relationships_found": 0,
        }

    # Step 3 — Cap columns for performance
    numeric_cols = numeric_cols[:8]

    # Step 4 — Compute pairwise correlations + regression slopes
    df_numeric = df[numeric_cols].dropna()

    if len(df_numeric) < 20:
        return {
            "status": "error",
            "error": "Not enough clean rows for causal analysis. Need at least 20.",
            "relationships": [],
            "relationships_found": 0,
        }

    relationships = []

    for col_a, col_b in combinations(numeric_cols, 2):
        x = df_numeric[col_a].values.astype(float)
        y = df_numeric[col_b].values.astype(float)

        # Pearson correlation
        if np.std(x) == 0 or np.std(y) == 0:
            continue

        corr = float(np.corrcoef(x, y)[0, 1])

        if abs(corr) < 0.2:
            continue  # skip weak relationships

        # Simple regression slope (rise / run normalized)
        slope = float(np.polyfit(x, y, 1)[0])

        # Estimate pct change: if x increases by 10%, how much does y change?
        x_mean = float(np.mean(x))
        y_mean = float(np.mean(y))
        if x_mean == 0:
            continue

        pct_change = (slope * x_mean * 0.10) / (y_mean + 1e-9) * 100

        confidence = round(min(abs(corr) * 100, 99), 1)
        direction  = "positive" if corr > 0 else "negative"

        relationships.append({
            "cause":       col_a,
            "effect":      col_b,
            "correlation": round(corr, 4),
            "direction":   direction,
            "confidence":  confidence,
            "pct_change":  round(pct_change, 2),
            "english": _interpret_relationship(col_a, col_b, corr, pct_change),
        })

    # Step 5 — Sort by confidence descending
    relationships.sort(key=lambda r: r["confidence"], reverse=True)

    # Step 6 — Highlight the top insight
    top_insight = ""
    if relationships:
        top = relationships[0]
        top_insight = top["english"]

    return {
        "status":               "success",
        "relationships_found":  len(relationships),
        "columns_analyzed":     numeric_cols,
        "top_insight":          top_insight,
        "relationships":        relationships[:10],
        "summary": {
            "positive_relationships": sum(1 for r in relationships if r["direction"] == "positive"),
            "negative_relationships": sum(1 for r in relationships if r["direction"] == "negative"),
            "avg_confidence":         round(
                sum(r["confidence"] for r in relationships) / len(relationships), 1
            ) if relationships else 0,
        },
    }