"""
Database connection and session management for the auction system.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from core.config import get_database_url
from models.auction import Base

# Create engine
engine = create_engine(get_database_url())

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database and create tables."""
    # Import all models to ensure they're registered with SQLAlchemy
    from models.user import User
    from models.story import Story, StoryNode
    from models.job import StoryJob
    from models.auction import Auction, Bid, AuctionItem, Category

    # Create all tables
    Base.metadata.create_all(bind=engine)


