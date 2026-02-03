import logging
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Setup logging
logger = logging.getLogger(__name__)

# Base Model
Base = declarative_base()


class UserFile(Base):
    __tablename__ = "user_files"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    # File Type: 'group' (persistent/admin) or 'temp' (session-tied)
    file_type = Column(String, nullable=False)
    # References to Azure Blob Storage or local path?
    # For this POC, we might store content in DB or assumed path.
    # Requirement: "Subir archivos asociados al usuario... limite 300mg"
    # We will just track metadata here. Content -> Azure Blob or Vector Store chunks.
    # The requirement says "files... persist between sessions".
    file_path = Column(String, nullable=True)
    user_id = Column(String, nullable=True)  # For 'temp' files owned by user
    created_at = Column(DateTime, default=datetime.utcnow)
    size_mb = Column(Integer, default=0)


# Checkpoints table is handled by LangGraph PostgresSaver usually,
# but we can verify its existence.


def get_db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback for dev if simple env var not set but local dev default exists?
        # Or raise error.
        raise ValueError("DATABASE_URL is not set.")
    return url


def init_db():
    """Initialize database tables."""
    engine = create_engine(get_db_url())
    Base.metadata.create_all(engine)
    logger.info("Database tables verified/created.")
    return engine


def get_session():
    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine)
    return Session()
