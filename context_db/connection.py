import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url() -> str:
    # Allow for a fallback for local dev, but require it for production
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return url

# Create engine with a pool size appropriate for a pipeline
engine = create_engine(
    get_database_url(), 
    pool_pre_ping=True,  # Checks if connection is alive before using it
    future=True,
    connect_args={"sslmode": os.environ.get("DB_SSLMODE", "require")},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@contextmanager
def get_session():
    """Context manager to ensure sessions are closed and rolled back on error."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()