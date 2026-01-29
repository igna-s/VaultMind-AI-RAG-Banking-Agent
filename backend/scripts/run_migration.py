from sqlalchemy import create_engine, text
from app.config import settings
import os

def run_migration():
    print(f"Connecting to database: {settings.DATABASE_URL.split('@')[1]}") # Hide password
    engine = create_engine(settings.DATABASE_URL)
    
    # Path to init.sql
    # Assuming script is run from backend/ dir
    init_sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Database/init.sql"))
    
    if not os.path.exists(init_sql_path):
        print(f"Error: init.sql not found at {init_sql_path}")
        return

    print(f"Reading init.sql from {init_sql_path}...")
    with open(init_sql_path, "r") as f:
        sql_script = f.read()

    # Split functionality might be needed if the driver doesn't support multiple statements in one go,
    # but sqlalchemy usually handles it or we can specifically use a raw connection.
    # Psycopg2 usually supports it.
    
    print("Executing migration...")
    with engine.connect() as connection:
        # We need to autocommit for some statements like CREATE EXTENSION or ALTER TYPE sometimes,
        # but here we can try running it as a block.
        # Alternatively, split by semicolon if needed, but DO blocks are tricky.
        # Let's try executing the whole script.
        try:
            connection.execute(text(sql_script))
            connection.commit()
            print("Migration successful!")
        except Exception as e:
            print(f"Migration failed: {e}")
            # Try splitting?
            # Creating extensions usually requires being outside a transaction block or specific handling.
            # But let's see.

if __name__ == "__main__":
    run_migration()
