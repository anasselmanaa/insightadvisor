from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend_core.storage import DB_PATH

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist"""
    import backend_core.models  # noqa: F401
    try:
        from backend_core.auth_service import User  # noqa: F401
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
