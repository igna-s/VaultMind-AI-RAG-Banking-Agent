from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("DATABASE_URL")
print(f"Connecting to {url}...")
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        print("Success:", res.fetchone())
except Exception as e:
    print("Error:", e)
