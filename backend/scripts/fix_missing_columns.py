import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def fix_missing_columns():
    print("🔧 Checking for missing 'created_at' in users table...")
    
    try:
        with engine.connect() as connection:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='created_at';
            """)
            result = connection.execute(check_query).fetchone()
            
            if result:
                print("✅ Column 'created_at' already exists.")
            else:
                # Add column
                print("➕ Adding column 'created_at'...")
                connection.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                connection.commit()
                print("✅ Successfully added 'created_at' column.")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_missing_columns()
