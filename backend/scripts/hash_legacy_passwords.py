from sqlmodel import Session, select, create_engine
from app.models import User
from app.auth import get_password_hash, pwd_context
from app.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_legacy_passwords():
    # Setup DB connection
    engine = create_engine(settings.DATABASE_URL)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        logger.info(f"Found {len(users)} users. Checking for legacy passwords...")
        
        updated_count = 0
        for user in users:
            # Check if password is NOT a valid bcrypt hash
            is_hashed = False
            try:
                if user.hashed_password and user.hashed_password.startswith("$2b$"):
                     # Basic check for bcrypt
                     is_hashed = True
                     # Optionally verify with passlib to be sure it's valid structure
                     # pwd_context.identify(user.hashed_password)
            except Exception:
                is_hashed = False
            
            # Since we know the previous default was "hashed_secret" or plain text, 
            # and proper bcrypt hashes start with $2b$ (or similar depending on rounds/salt)
            # We can also rely on passlib identify, but for this specific "hashed_secret" case:
            
            if user.hashed_password == "hashed_secret":
                logger.info(f"Hashing legacy default password for user {user.email}")
                user.hashed_password = get_password_hash("password") # Default password
                session.add(user)
                updated_count += 1
            elif not user.hashed_password.startswith("$"): # Very basic check for plain text
                logger.info(f"Hashing potential plain text password for user {user.email}")
                try:
                    user.hashed_password = get_password_hash(user.hashed_password)
                    session.add(user)
                    updated_count += 1
                except ValueError as e:
                    logger.warning(f"Failed to hash password for {user.email}: {e}. Resetting to default 'password'.")
                    user.hashed_password = get_password_hash("password")
                    session.add(user)
                    updated_count += 1
                
        session.commit()
        logger.info(f"Migration complete. Updated {updated_count} users.")

if __name__ == "__main__":
    hash_legacy_passwords()
