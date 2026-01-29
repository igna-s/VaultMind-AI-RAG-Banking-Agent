from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(".env")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "password")
host = os.getenv("POSTGRES_HOST", "127.0.0.1")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "rag_db")

url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
print(f"Connecting to {url}...")
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        print("Success:", res.fetchone())
except Exception as e:
    print("Error:", e)
