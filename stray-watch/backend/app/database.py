from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

# This is the connection string to your PostgreSQL database.
# It reads from your .env file so you never hardcode passwords in code.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/strawatch"
)

# The engine is the actual connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory — every time you call SessionLocal()
# you get a fresh database session to run queries with
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """
    Call this once on startup.
    Reads all your models.py classes and creates the actual tables
    in PostgreSQL if they don't exist yet.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    This is a FastAPI dependency — routes call this to get a
    database session, use it, then close it cleanly afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()