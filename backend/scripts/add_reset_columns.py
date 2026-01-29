import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def add_reset_columns():
    print("🚀 Adding password reset columns to users table...")
    
    try:
        with engine.connect() as connection:
            # Check and Add reset_token
            check_token = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token';")
            if not connection.execute(check_token).fetchone():
                print("➕ Adding 'reset_token' column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN reset_token TEXT;"))
            else:
                print("✅ 'reset_token' already exists.")

            # Check and Add reset_token_expires_at
            check_expires = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token_expires_at';")
            if not connection.execute(check_expires).fetchone():
                print("➕ Adding 'reset_token_expires_at' column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires_at TIMESTAMP;"))
            else:
                print("✅ 'reset_token_expires_at' already exists.")
                
            connection.commit()
            print("✅ Migration completed successfully.")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_reset_columns()
