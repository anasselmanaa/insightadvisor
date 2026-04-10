from fastapi import APIRouter, HTTPException, Query
import json

from backend_core.storage import stock_report_path
from backend_core.stock_service import analyze_stock

router = APIRouter(tags=["Stock"])


@router.get("/stock/{ticker}")
def get_stock_analysis(
    ticker:        str,
    period:        str = Query(default="1y",  description="Data period: 1mo, 3mo, 6mo, 1y, 2y"),
    forecast_days: int = Query(default=30, ge=7, le=90),
):
    try:
        result = analyze_stock(
            ticker=ticker,
            period=period,
            forecast_days=forecast_days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stock analysis failed: {str(e)}"
        )

    # Save report
    out = stock_report_path(ticker)
    out.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return {
        "status": "success",
        "stock":  result,
        "saved_report": str(out)
    }