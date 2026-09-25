"""
RevenueAI 360 - Database Engine & Session Management
Provides dynamic database connection handling for PostgreSQL (production/docker)
and SQLite (local dev/tests), with automatic schema initialization.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from domain.models import Base

# Configuration with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./revenueai.db")

# SQLite needs check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(target_engine=engine):
    """Initialize database tables and extensions."""
    if str(target_engine.url).startswith("postgresql"):
        try:
            with target_engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception as e:
            print(f"[DB Warning] Could not enable pgvector extension: {e}")

    Base.metadata.create_all(bind=target_engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
