from sqlmodel import Session, text

from app.database import engine


def verify_all_existing_users():
    with Session(engine) as session:
        # Update all users to be verified
        # This prevents existing users from being locked out by the new verification requirement
        statement = text("UPDATE users SET is_verified = TRUE WHERE is_verified IS NULL OR is_verified = FALSE")
        session.exec(statement)
        session.commit()
        print("Successfully verified all existing users.")


if __name__ == "__main__":
    verify_all_existing_users()
