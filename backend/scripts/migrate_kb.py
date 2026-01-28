from sqlmodel import Session, text, SQLModel
from app.database import engine

def migrate():
    print("Starting migration...")
    with Session(engine) as session:
        # 1. Create new tables first (so FK target exists)
        print("Creating new tables...")
        SQLModel.metadata.create_all(engine)
        
        # 2. Add column to documents if it doesn't exist
        try:
            session.exec(text("ALTER TABLE documents ADD COLUMN knowledge_base_id INTEGER REFERENCES knowledge_bases(id)"))
            session.commit()
            print("Added knowledge_base_id column to documents.")
        except Exception as e:
            # If column exists, it throws. Keep going.
            print(f"Skipping column add (check logs): {e}")
            session.rollback()
    
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
