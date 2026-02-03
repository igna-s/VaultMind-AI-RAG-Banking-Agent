from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in settings")

# Ensure asyncpg or psycopg2 driver use (we use psycopg2 via sqlalchemy default for sync)
connect_args = {"connect_timeout": 5} # Fail fast (5s) if DB is unreachable
if settings.APP_MODE != "DEV":
    connect_args["sslmode"] = "require"

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    from sqlalchemy import text
    
    # Run init.sql (Idempotent Schema Updates)
    init_sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Database", "init.sql")
    if os.path.exists(init_sql_path):
        try:
             with open(init_sql_path, "r") as f:
                sql_script = f.read()
                with engine.connect() as connection:
                    connection.execute(text(sql_script))
                    connection.commit()
        except Exception as e:
            logger.warning(f"Failed to execute init.sql: {e}")

    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    SQLModel.metadata.create_all(engine)
    
    # Run migrations for logging tables (idempotent)
    _run_logging_migrations()

def _run_logging_migrations():
    """
    Run idempotent migrations for logging tables.
    This ensures the schema is up to date even if tables were created before
    the new columns/tables were added to the models.
    """
    from sqlalchemy import text
    
    migration_sql = """
    -- Add user_id column to token_usage if it doesn't exist
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='token_usage' AND column_name='user_id'
        ) THEN
            ALTER TABLE token_usage ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
        END IF;
    END $$;

    -- Create user_logs table if not exists
    CREATE TABLE IF NOT EXISTS user_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        event VARCHAR(50) NOT NULL,
        details JSONB DEFAULT '{}',
        ip_address VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create error_logs table if not exists
    CREATE TABLE IF NOT EXISTS error_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        path TEXT,
        method VARCHAR(10),
        error_message TEXT NOT NULL,
        stack_trace TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes if not exist
    CREATE INDEX IF NOT EXISTS ix_token_usage_user ON token_usage(user_id);
    CREATE INDEX IF NOT EXISTS ix_user_logs_user ON user_logs(user_id);
    CREATE INDEX IF NOT EXISTS ix_user_logs_created ON user_logs(created_at);
    CREATE INDEX IF NOT EXISTS ix_error_logs_created ON error_logs(created_at);
    """
    
    try:
        with engine.connect() as connection:
            connection.execute(text(migration_sql))
            connection.commit()
            logger.info("Logging migrations completed successfully")
    except Exception as e:
        logger.warning(f"Failed to run logging migrations: {e}")

def get_session():
    with Session(engine) as session:
        yield session
