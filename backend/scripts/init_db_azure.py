import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path to be able to import app.config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("Initializing Azure Database...")

    # Load environment variables from Database/.env
    # We walk up from scripts/ -> backend/ -> TheDefinitiveProyect/ -> Database/.env
    # script location: /workspace/TheDefinitiveProyect/backend/scripts/init_db_azure.py
    # target env: /workspace/TheDefinitiveProyect/Database/.env
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    database_env_path = os.path.join(project_root, "Database", ".env")
    
    print(f"Loading .env from: {database_env_path}")
    if not os.path.exists(database_env_path):
        print(f"Error: {database_env_path} not found!")
        sys.exit(1)
        
    load_dotenv(database_env_path)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment!")
        sys.exit(1)
        
    print("DATABASE_URL found.")
    
    # Read init.sql
    init_sql_path = os.path.join(project_root, "Database", "init.sql")
    print(f"Reading init.sql from: {init_sql_path}")
    if not os.path.exists(init_sql_path):
        print(f"Error: {init_sql_path} not found!")
        sys.exit(1)
        
    with open(init_sql_path, "r") as f:
        sql_script = f.read()
        
    # Connect and Execute
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            print("Connected to database...")
            # Execute the script
            # We split by statement if needed, but sqlalchemy `text` might handle it or we can execute raw
            # However, init.sql contains DO blocks and other things that might be better executed as a whole or carefully split.
            # Simple approach: execute the whole block if possible, or split by ';' if simple.
            # Given the content has $$ blocks, simple splitting by ; is dangerous.
            # Best to use a raw execution.
            
            connection.execute(text(sql_script))
            connection.commit()
            print("Successfully executed init.sql")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
