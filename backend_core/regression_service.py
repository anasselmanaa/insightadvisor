import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Returns first matching column or None if not found"""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label-encode all categorical (object) columns.
    Needed because LinearRegression only works with numbers.
    """
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    return df


def run_linear_regression(
    df: pd.DataFrame,
    target_col: str = None
) -> dict:
    """
    Full Linear Regression pipeline:
    1. Auto-detect or use specified target column
    2. Select numeric + encoded categorical features
    3. Train/test split (80/20)
    4. Fit LinearRegression
    5. Calculate R², MAE, RMSE
    6. Return feature importance (coefficients)
    7. Return actual vs predicted for scatter plot
    """
    df = _normalize_columns(df)

    # Step 1 — Determine target column
    if target_col:
        target_col = target_col.lower().replace(" ", "_")
        if target_col not in df.columns:
            raise ValueError(
                f"Target column '{target_col}' not found. "
                f"Available: {list(df.columns)}"
            )
    else:
        # Auto-detect: prefer revenue, then price, then first numeric
        target_col = _pick_column(
            df, ["revenue", "price", "unitprice", "sales", "amount"]
        )
        if not target_col:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if not numeric_cols:
                raise ValueError("No numeric columns found for regression.")
            target_col = numeric_cols[-1]

    # Step 2 — Prepare features
    # Drop non-useful columns
    drop_cols = [
        target_col,
        *[c for c in df.columns if "date" in c or "id" in c or "invoice" in c]
    ]
    feature_df = df.drop(
        columns=[c for c in drop_cols if c in df.columns],
        errors="ignore"
    )

    # Encode categoricals
    feature_df = _encode_categoricals(feature_df)

    # Keep only numeric
    feature_df = feature_df.select_dtypes(include="number")

    if feature_df.empty or feature_df.shape[1] == 0:
        raise ValueError("No valid feature columns found for regression.")

    # Align target
    target = df[target_col]
    valid_idx = feature_df.dropna().index.intersection(target.dropna().index)

    if len(valid_idx) < 50:
        raise ValueError(
            f"Not enough valid rows for regression: {len(valid_idx)}. Need at least 50."
        )

    X = feature_df.loc[valid_idx].values
    y = target.loc[valid_idx].values

    # Step 3 — Train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Step 4 — Fit model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Step 5 — Predictions + Metrics
    y_pred = model.predict(X_test)

    r2   = float(r2_score(y_test, y_pred))
    mae  = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    # Step 6 — Feature importance (coefficients)
    feature_names = feature_df.columns.tolist()
    coefficients  = model.coef_.tolist()

    feature_importance = sorted(
        [
            {
                "feature":     name,
                "coefficient": round(coef, 4),
                "abs_impact":  round(abs(coef), 4),
            }
            for name, coef in zip(feature_names, coefficients)
        ],
        key=lambda x: x["abs_impact"],
        reverse=True
    )

    # Step 7 — Actual vs Predicted (sample max 200 points for chart)
    sample_size = min(200, len(y_test))
    indices     = np.random.choice(len(y_test), sample_size, replace=False)

    actual_vs_predicted = [
        {
            "actual":    round(float(y_test[i]), 2),
            "predicted": round(float(y_pred[i]), 2),
        }
        for i in sorted(indices)
    ]

    return {
        "target_column":      target_col,
        "feature_columns":    feature_names,
        "train_size":         len(X_train),
        "test_size":          len(X_test),
        "metrics": {
            "r2":   round(r2,   4),
            "mae":  round(mae,  2),
            "rmse": round(rmse, 2),
        },
        "intercept":          round(float(model.intercept_), 4),
        "feature_importance": feature_importance,
        "actual_vs_predicted": actual_vs_predicted,
        "interpretation": (
            f"The model explains {round(r2 * 100, 1)}% of variance in {target_col}. "
            f"Average prediction error: {round(mae, 2)} units."
        )
    }