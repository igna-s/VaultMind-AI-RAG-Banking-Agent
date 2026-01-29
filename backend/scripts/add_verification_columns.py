from sqlmodel import Session, text
from app.database import engine

def add_verification_columns():
    with Session(engine) as session:
        # Check if columns exist
        try:
            session.exec(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            print("Added is_verified column")
        except Exception as e:
            print(f"is_verified column might already exist: {e}")
            session.rollback()

        try:
            session.exec(text("ALTER TABLE users ADD COLUMN verification_code VARCHAR"))
            print("Added verification_code column")
        except Exception as e:
            print(f"verification_code column might already exist: {e}")
            session.rollback()
            
        session.commit()

if __name__ == "__main__":
    add_verification_columns()
