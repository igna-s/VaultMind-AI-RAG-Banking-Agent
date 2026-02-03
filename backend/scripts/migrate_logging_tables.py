#!/usr/bin/env python3
"""
Migration script to add missing tables and columns for logging functionality.
Run this on Azure PostgreSQL to fix the admin panel.
"""

import os
import sys
from dotenv import load_dotenv

# Load env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../.env")
load_dotenv(env_path)

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    sys.exit(1)

print(f"🔗 Connecting to Azure PostgreSQL...")

engine = create_engine(DATABASE_URL)

MIGRATION_SQL = """
-- ============================================
-- Migration: Add logging tables and columns
-- ============================================

-- 1. Add user_id column to token_usage if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='token_usage' AND column_name='user_id'
    ) THEN
        ALTER TABLE token_usage ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added user_id column to token_usage';
    ELSE
        RAISE NOTICE 'user_id column already exists in token_usage';
    END IF;
END $$;

-- 2. Create user_logs table
CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create error_logs table
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    path TEXT,
    method VARCHAR(10),
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create indexes
CREATE INDEX IF NOT EXISTS ix_token_usage_user ON token_usage(user_id);
CREATE INDEX IF NOT EXISTS ix_user_logs_user ON user_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_user_logs_created ON user_logs(created_at);
CREATE INDEX IF NOT EXISTS ix_error_logs_created ON error_logs(created_at);

-- Done!
SELECT 'Migration completed successfully!' as status;
"""

try:
    with engine.connect() as conn:
        # Execute migration
        conn.execute(text(MIGRATION_SQL))
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify tables exist
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_logs', 'error_logs', 'token_usage')
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"✅ Tables verified: {tables}")
        
        # Verify user_id column in token_usage
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'token_usage' AND column_name = 'user_id';
        """))
        columns = [row[0] for row in result.fetchall()]
        if columns:
            print(f"✅ Column token_usage.user_id exists")
        else:
            print(f"⚠️ Column token_usage.user_id NOT found")
            
except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)
