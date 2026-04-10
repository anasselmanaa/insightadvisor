from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_core.routes_upload import router as upload_router
from backend_core.routes_eda import router as eda_router
from backend_core.routes_kmeans import router as kmeans_router
from backend_core.routes_export import router as export_router
from backend_core.routes_arima import router as arima_router
from backend_core.routes_regression import router as regression_router
from backend_core.routes_apriori import router as apriori_router
from backend_core.routes_stock import router as stock_router
from backend_core.routes_anomaly import router as anomaly_router
from backend_core.routes_ai import router as ai_router
from backend_core.routes_auth import router as auth_router
from backend_core.routes_audit import router as audit_router
from backend_core.database import init_db

app = FastAPI(title="RetailIQ Backend", version="2.0")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(upload_router)
app.include_router(eda_router)
app.include_router(kmeans_router)
app.include_router(export_router)
app.include_router(arima_router)
app.include_router(regression_router)
app.include_router(apriori_router)
app.include_router(stock_router)
app.include_router(anomaly_router)
app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "RetailIQ Backend is running"}
