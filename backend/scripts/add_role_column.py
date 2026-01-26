import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def add_role_column():
    print("🚀 Adding 'role' column to users table...")
    
    try:
        with engine.connect() as connection:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role';
            """)
            result = connection.execute(check_query).fetchone()
            
            if result:
                print("✅ Column 'role' already exists.")
            else:
                # Add column
                print("➕ Adding column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';"))
                
                # Update existing admin (the one we created in main.py usually) or just update specific email
                print("👑 promoting admin@bank.com to admin...")
                connection.execute(text("UPDATE users SET role = 'admin' WHERE email = 'admin@bank.com';"))
                
                connection.commit()
                print("✅ Successfully added 'role' column and updated admin.")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_role_column()
