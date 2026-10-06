"""
Database connection and session management using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from app.config import DATABASE_URL

# SQLite requires connect_args={"check_same_thread": False} for multi-threaded apps like Streamlit
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()


def init_db():
    """Initializes tables in database."""
    import app.data.entities  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)


def get_db():
    """Provides database session context."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
