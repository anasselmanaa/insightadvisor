from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from backend_core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id            = Column(String, primary_key=True, index=True)
    filename      = Column(String, nullable=False)
    upload_date   = Column(DateTime, server_default=func.now())
    dataset_type  = Column(String, default="generic")
    raw_rows      = Column(Integer)
    raw_cols      = Column(Integer)
    cleaned_rows  = Column(Integer)
    cleaned_cols  = Column(Integer)
    quality_score = Column(Integer)


class AnalysisResult(Base):
    __tablename__ = "analyses"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id    = Column(String, index=True)
    analysis_type = Column(String)
    result_path   = Column(String)
    created_at    = Column(DateTime, server_default=func.now())
    status        = Column(String, default="success")


class ClusteringResult(Base):
    __tablename__ = "clustering_results"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id       = Column(String, index=True)
    n_clusters       = Column(Integer)
    silhouette_score = Column(Float)
    davies_bouldin   = Column(Float)
    created_at       = Column(DateTime, server_default=func.now())


class ForecastingResult(Base):
    __tablename__ = "forecasting_results"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id    = Column(String, index=True)
    model         = Column(String)
    forecast_days = Column(Integer)
    rmse          = Column(Float)
    mape          = Column(Float)
    trend         = Column(String)
    created_at    = Column(DateTime, server_default=func.now())


class RegressionResult(Base):
    __tablename__ = "regression_results"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, index=True)
    target_col = Column(String)
    r_squared  = Column(Float)
    mae        = Column(Float)
    rmse       = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id      = Column(String, index=True)
    anomalies_found = Column(Integer)
    contamination   = Column(Float)
    created_at      = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_log"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, index=True)
    action     = Column(String)
    details    = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
