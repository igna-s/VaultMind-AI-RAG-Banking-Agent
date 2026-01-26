import os
import sys
from sqlalchemy import text
from collections import defaultdict

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from app.config import settings

def inspect_schema():
    print(f"\n🔍 Inspecting Database Schema: {settings.POSTGRES_DB}")
    print(f"URL: {settings.DATABASE_URL.split('@')[-1]}") # Hide credentials
    print("="*60)
    
    try:
        with engine.connect() as connection:
            # query to get all tables and their columns
            query = text("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                ORDER BY table_name, ordinal_position;
            """)
            
            result = connection.execute(query)
            schema = defaultdict(list)
            
            for row in result:
                table_name, col_name, dtype, nullable = row
                schema[table_name].append((col_name, dtype, nullable))
                
            if not schema:
                print("❌ No tables found in 'public' schema.")
                return

            for table, columns in schema.items():
                print(f"\n📂 Table: {table}")
                print(f"   {'-'*50}")
                print(f"   {'Column':<20} | {'Type':<15} | {'Nullable'}")
                print(f"   {'-'*50}")
                for col, dtype, nullable in columns:
                    print(f"   {col:<20} | {dtype:<15} | {nullable}")
            
            print("\n" + "="*60)
            print("✅ Inspection Complete.")
                
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    inspect_schema()
