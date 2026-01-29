from sqlmodel import Session, select, text
from app.database import engine
from app.models import User

def revert_legacy_verification():
    with Session(engine) as session:
        # Set is_verified = FALSE for users who have NO verification code.
        # These are assumed to be legacy users (or broken registrations).
        # New logic allows them to login if verified=False AND code=None.
        statement = text("UPDATE users SET is_verified = FALSE WHERE verification_code IS NULL")
        session.exec(statement)
        session.commit()
        print("Successfully reverted verification status for legacy users.")

if __name__ == "__main__":
    revert_legacy_verification()
