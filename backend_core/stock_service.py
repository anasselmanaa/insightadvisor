import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    Returns daily OHLCV data.
    """
    stock = yf.Ticker(ticker.upper())
    df = None
    for params in [
        {"period": period, "auto_adjust": True},
        {"period": period, "auto_adjust": False},
        {"period": "1y", "auto_adjust": True},
    ]:
        try:
            tmp = stock.history(**params)
            tmp = tmp.dropna()
            if not tmp.empty and len(tmp) > 5:
                df = tmp
                break
        except Exception:
            continue
    if df is None:
        df = stock.history(period=period)

    if df.empty:
        raise ValueError(
            f"No data found for ticker '{ticker}'. "
            f"Please check the ticker symbol is correct."
        )

    df = df.reset_index()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # Keep only needed columns
    cols = ["date", "open", "high", "low", "close", "volume"]
    df   = df[[c for c in cols if c in df.columns]]

    # Clean date
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)

    return df


def get_stock_info(ticker: str) -> dict:
    """Get basic stock information"""
    try:
        stock = yf.Ticker(ticker.upper())
        info  = stock.info
        return {
            "name":        info.get("longName",      ticker),
            "sector":      info.get("sector",         "N/A"),
            "industry":    info.get("industry",       "N/A"),
            "currency":    info.get("currency",       "USD"),
            "country":     info.get("country",        "N/A"),
            "market_cap":  info.get("marketCap",      None),
            "description": info.get("longBusinessSummary", "")[:300],
        }
    except Exception:
        return {"name": ticker, "sector": "N/A", "industry": "N/A",
                "currency": "USD", "country": "N/A"}


def run_stock_arima(
    close_prices: pd.Series,
    forecast_days: int = 30
) -> dict:
    """
    Run ARIMA on stock closing prices.
    Returns forecast with confidence intervals.
    """
    series = close_prices.dropna()

    if len(series) < 30:
        raise ValueError(f"Not enough data: {len(series)} days. Need 30+.")

    # Fit ARIMA(1,1,1)
    model  = ARIMA(series, order=(1, 1, 1))
    fitted = model.fit()

    # Forecast
    forecast_result = fitted.get_forecast(steps=forecast_days)
    forecast_mean   = forecast_result.predicted_mean
    conf_int        = forecast_result.conf_int(alpha=0.05)

    # Metrics
    fitted_values = fitted.fittedvalues
    residuals     = series - fitted_values
    rmse          = float(np.sqrt(np.mean(residuals ** 2)))

    mask = series != 0
    mape = (
        float(np.mean(np.abs(residuals[mask] / series[mask])) * 100)
        if mask.sum() > 0 else None
    )

    # Build forecast list
    last_date = pd.to_datetime(series.index[-1]) \
        if not isinstance(series.index[-1], str) \
        else pd.to_datetime(str(series.index[-1]))

    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=forecast_days,
        freq="B"  # Business days only
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

    trend = (
        "increasing"
        if forecast_mean.iloc[-1] > forecast_mean.iloc[0]
        else "decreasing"
    )

    return {
        "metrics": {
            "rmse": round(rmse, 2),
            "mape": round(mape, 2) if mape else None,
        },
        "trend":         trend,
        "forecast":      forecast_data,
        "forecast_days": forecast_days,
    }


def analyze_stock(
    ticker:        str,
    period:        str = "1y",
    forecast_days: int = 30
) -> dict:
    """
    Full stock analysis pipeline:
    1. Fetch stock data from Yahoo Finance
    2. Get stock info (name, sector, etc.)
    3. Calculate key statistics
    4. Run ARIMA forecast on closing price
    5. Return everything for frontend charts
    """

    # Step 1 — Fetch data
    df = fetch_stock_data(ticker, period)

    # Step 2 — Get info
    info = get_stock_info(ticker)

    # Step 3 — Key statistics
    close = df["close"]
    stats = {
        "current_price":  round(float(close.iloc[-1]), 2),
        "previous_price": round(float(close.iloc[-2]), 2) if len(close) > 1 else None,
        "price_change":   round(float(close.iloc[-1] - close.iloc[-2]), 2) if len(close) > 1 else None,
        "pct_change":     round(float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100), 2) if len(close) > 1 else None,
        "period_high":    round(float(df["high"].max()), 2) if "high" in df.columns else None,
        "period_low":     round(float(df["low"].min()),  2) if "low"  in df.columns else None,
        "avg_volume":     int(df["volume"].mean())          if "volume" in df.columns else None,
        "total_days":     len(df),
    }

    # Step 4 — ARIMA forecast
    close_series = pd.Series(
        df["close"].values,
        index=pd.to_datetime(df["date"])
    )
    arima_result = run_stock_arima(close_series, forecast_days)

    # Step 5 — Historical data for candlestick chart
    historical = df.to_dict(orient="records")

    return {
        "ticker":     ticker.upper(),
        "period":     period,
        "info":       info,
        "stats":      stats,
        "historical": historical,
        "forecast":   arima_result,
    }