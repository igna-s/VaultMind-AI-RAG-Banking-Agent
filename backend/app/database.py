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
connect_args = {}
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

def get_session():
    with Session(engine) as session:
        yield session
