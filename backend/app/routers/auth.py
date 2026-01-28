from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from app.auth import (
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    Token,
    get_password_hash
)
from app.limiter import limiter
from pydantic import BaseModel
from fastapi import Response

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    email: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    # Check existing
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        status="active",
        role="user"
    )
    session.add(new_user)
    session.commit()
    
    return {"message": "User created successfully"}

@router.post("/token", response_model=Token)
# @limiter.limit("30/minute")
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    print(f"DEBUG: Login Request Received for user: {form_data.username}")
    print(f"DEBUG: Headers: {request.headers}")
    try:
        print(f"DEBUG: Login attempt for {form_data.username}")
        print(f"DEBUG: Password received length: {len(form_data.password)}")
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            print("DEBUG: Authentication failed - Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Set HttpOnly Cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False, # Set to True in PROD with HTTPS
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "role": user.role
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, 500
        print(f"CRITICAL ERROR IN LOGIN: {e}")
        with open("error.log", "a") as f:
            f.write(f"CRITICAL ERROR IN LOGIN: {e}\n")
            traceback.print_exc(file=f)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )
