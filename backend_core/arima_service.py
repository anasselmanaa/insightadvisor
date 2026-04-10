import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings("ignore")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Same helper as kmeans_service — consistent style"""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str:
    """Same helper as kmeans_service"""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"None of these columns found: {candidates}. "
        f"Available: {list(df.columns)}"
    )


def check_stationarity(series: pd.Series) -> dict:
    """
    Augmented Dickey-Fuller test.
    p-value < 0.05 = stationary = ARIMA can run directly.
    p-value >= 0.05 = non-stationary = differencing needed (d=1).
    """
    result = adfuller(series.dropna())
    is_stationary = bool(result[1] < 0.05)

    return {
        "is_stationary": is_stationary,
        "adf_statistic": round(float(result[0]), 4),
        "p_value":       round(float(result[1]), 4),
        "interpretation": (
            "Series is stationary — ARIMA ready"
            if is_stationary
            else "Series is non-stationary — differencing applied (d=1)"
        )
    }


def build_time_series(df: pd.DataFrame) -> pd.Series:
    """
    Convert transaction-level data to daily revenue time series.
    Works with any column naming convention.
    """
    df = _normalize_columns(df)

    date_col  = _pick_column(df, ["invoicedate","invoice_date","date","order_date","purchase_date","manufacturing_date","created_at"])
    qty_col   = _pick_column(df, ["quantity","qty","stock_quantity","units","count","volume","stock"])
    price_col = _pick_column(df, ["price", "unitprice", "unit_price"])

    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    # Convert numeric
    df[qty_col]   = pd.to_numeric(df[qty_col],   errors="coerce")
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[qty_col, price_col])

    # Keep valid sales only
    df = df[(df[qty_col] > 0) & (df[price_col] >= 0)]

    # Revenue column
    if "revenue" in df.columns:
        rev_col = "revenue"
    else:
        df["revenue"] = df[qty_col] * df[price_col]
        rev_col = "revenue"

    # Aggregate to daily
    daily = (
        df.groupby(df[date_col].dt.date)[rev_col]
        .sum()
        .reset_index()
    )
    daily.columns = ["date", "revenue"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").set_index("date")

    # Fill missing dates with 0
    full_range = pd.date_range(
        start=daily.index.min(),
        end=daily.index.max(),
        freq="D"
    )
    daily = daily.reindex(full_range, fill_value=0)

    return daily["revenue"]


def run_arima_forecast(
    df: pd.DataFrame,
    forecast_days: int = 30,
    p: int = 1,
    d: int = 1,
    q: int = 1
) -> dict:
    """
    Full ARIMA pipeline:
    1. Build daily revenue time series
    2. Check stationarity (ADF test)
    3. Auto-adjust d if series is non-stationary
    4. Fit ARIMA model
    5. Forecast next N days with 95% confidence intervals
    6. Calculate RMSE + MAPE
    7. Return everything needed for frontend charts
    """

    # Step 1 — Build time series
    series = build_time_series(df)

    if len(series) < 30:
        raise ValueError(
            f"Not enough data for forecasting. "
            f"Need at least 30 days, got {len(series)}."
        )

    # Step 2 — Stationarity check
    stationarity = check_stationarity(series)

    # Step 3 — Auto-adjust d
    if not stationarity["is_stationary"] and d == 0:
        d = 1

    # Step 4 — Fit ARIMA
    model  = ARIMA(series, order=(p, d, q))
    fitted = model.fit()

    # Step 5 — Forecast with confidence intervals
    forecast_result = fitted.get_forecast(steps=forecast_days)
    forecast_mean   = forecast_result.predicted_mean
    conf_int        = forecast_result.conf_int(alpha=0.05)

    # Step 6 — Evaluation metrics on training data
    fitted_values = fitted.fittedvalues
    residuals     = series - fitted_values

    rmse = float(np.sqrt(np.mean(residuals ** 2)))

    mask = series != 0
    mape = (
        float(np.mean(np.abs(residuals[mask] / series[mask])) * 100)
        if mask.sum() > 0 else None
    )

    # Step 7 — Build response

    # Historical data for chart (last 90 days max to keep response small)
    historical_series = series.tail(90)
    historical = [
        {
            "date":    str(date.date()),
            "revenue": round(float(val), 2)
        }
        for date, val in historical_series.items()
    ]

    # Forecast data for chart
    forecast_dates = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )
    forecast_data = [
        {
            "date":        str(date.date()),
            "forecast":    round(float(forecast_mean.iloc[i]), 2),
            "lower_bound": round(float(conf_int.iloc[i, 0]), 2),
            "upper_bound": round(float(conf_int.iloc[i, 1]), 2),
        }
        for i, date in enumerate(forecast_dates)
    ]

    # Summary
    total_forecast     = round(float(forecast_mean.sum()), 2)
    avg_daily_forecast = round(float(forecast_mean.mean()), 2)
    trend = (
        "increasing"
        if forecast_mean.iloc[-1] > forecast_mean.iloc[0]
        else "decreasing"
    )

    return {
        "model":        f"ARIMA({p},{d},{q})",
        "forecast_days": forecast_days,
        "stationarity": stationarity,
        "metrics": {
            "rmse": round(rmse, 2),
            "mape": round(mape, 2) if mape else None,
        },
        "summary": {
            "total_forecast_revenue": total_forecast,
            "avg_daily_forecast":     avg_daily_forecast,
            "trend":                  trend,
            "last_known_date":   str(series.index[-1].date()),
            "forecast_start":    str(forecast_dates[0].date()),
            "forecast_end":      str(forecast_dates[-1].date()),
            "historical_days":   len(series),
        },
        "historical": historical,
        "forecast":   forecast_data,
    }