from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load env from backend root
current_dir = os.path.dirname(os.path.abspath(__file__))
# .env is in backend/, which is parent of app/
dotenv_path = os.path.join(os.path.dirname(current_dir), '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL env var is not set")

# Ensure asyncpg or psycopg2 driver use (we use psycopg2 via sqlalchemy default for sync)
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from sqlalchemy import text
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
