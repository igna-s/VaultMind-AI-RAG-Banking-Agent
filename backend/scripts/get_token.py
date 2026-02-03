from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.auth import create_access_token
from datetime import timedelta

def get_admin_token():
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin@bank.com")).first()
        if not user:
            print("Admin user not found")
            return
        
        token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=5))
        print(f"TOKEN: {token}")

if __name__ == "__main__":
    get_admin_token()
