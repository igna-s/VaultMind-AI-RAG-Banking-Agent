from sqlmodel import Session, select, text
from app.database import engine
from app.models import ChatSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_sessions():
    """
    Migration script to:
    1. Add updated_at column to chat_sessions table if it doesn't exist
    2. Backfill updated_at with created_at for existing records
    """
    logger.info("Starting migration: Adding updated_at to chat_sessions")
    
    with Session(engine) as session:
        # 1. Add column if not exists
        try:
            # Check if column exists
            # This is a postgres specific check
            result = session.exec(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='chat_sessions' AND column_name='updated_at'"
            )).first()
            
            if not result:
                logger.info("Column 'updated_at' not found. Adding it...")
                session.exec(text("ALTER TABLE chat_sessions ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE"))
                session.commit()
                logger.info("Column added successfully.")
            else:
                logger.info("Column 'updated_at' already exists.")
                
        except Exception as e:
            logger.error(f"Error adding column: {e}")
            session.rollback()
            return

        # 2. Backfill null values
        try:
            logger.info("Backfilling NULL updated_at values with created_at...")
            # We can do this in one SQL update for efficiency
            session.exec(text("UPDATE chat_sessions SET updated_at = created_at WHERE updated_at IS NULL"))
            session.commit()
            logger.info("Backfill completed.")
            
        except Exception as e:
            logger.error(f"Error backfilling data: {e}")
            session.rollback()

if __name__ == "__main__":
    migrate_sessions()
