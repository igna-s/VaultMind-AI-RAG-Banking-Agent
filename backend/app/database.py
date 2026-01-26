from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

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
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
