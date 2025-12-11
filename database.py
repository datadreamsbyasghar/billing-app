from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
else:
    raise RuntimeError("DATABASE_URL is not set")

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database session not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()