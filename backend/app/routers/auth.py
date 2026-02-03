import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests

# Google Auth
from google.oauth2 import id_token
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from app.config import settings
from app.database import get_session
from app.limiter import limiter
from app.models import KnowledgeBase, User, UserKnowledgeBaseLink, UserLog

# Email service
from app.services.email import send_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


def validate_password_strength(password: str) -> bool:
    """
    Validates that password has at least 10 chars, uppercase, lowercase,
    number, and special character.
    """
    if len(password) < 10:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


class UserRegister(BaseModel):
    email: str
    password: str


class VerifyEmailRequest(BaseModel):
    email: str
    code: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class GoogleLoginRequest(BaseModel):
    credential: str  # The JWT ID token from Google


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    try:
        # Validate password
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe tener al menos 10 caracteres, una mayúscula, una minúscula, un número y un carácter especial.",
            )

        # Check existing
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Generate verification code (Secure Random)
        verification_code = "".join(secrets.choice(string.digits) for _ in range(6))

        # Create user
        new_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            status="active",
            role="user",
            is_verified=False,
            verification_code=verification_code,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Assign default Knowledge Bases
        default_kbs = session.exec(select(KnowledgeBase).where(KnowledgeBase.is_default)).all()
        for kb in default_kbs:
            link = UserKnowledgeBaseLink(user_id=new_user.id, knowledge_base_id=kb.id)
            session.add(link)
        session.commit()

        # Send verification email in background
        background_tasks.add_task(send_verification_email, new_user.email, verification_code)

        return {"message": "Registro exitoso. Revisa tu email para el código de verificación.", "email": new_user.email}
    except HTTPException:
        raise
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.is_verified:
        return {"message": "Email ya verificado"}

    if user.verification_code != request.code:
        raise HTTPException(status_code=400, detail="Código inválido")

    user.is_verified = True
    user.verification_code = None
    session.add(user)
    session.commit()

    return {"message": "Email verificado exitosamente"}


@router.post("/resend-verification-code")
@limiter.limit("5/minute")
async def resend_verification_code(
    request: Request,
    payload: ForgotPasswordRequest,  # reusing email model
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "Si el email existe, se ha enviado un código."}

    if user.is_verified:
        return {"message": "Email ya verificado."}

    # Generate new code
    # Generate new code (Secure Random)
    verification_code = "".join(secrets.choice(string.digits) for _ in range(6))
    user.verification_code = verification_code
    session.add(user)
    session.commit()

    # Send email in background
    background_tasks.add_task(send_verification_email, user.email, verification_code)

    return {"message": "Código reenviado exitosamente."}


@router.post("/token", response_model=Token)
# @limiter.limit("30/minute")
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    try:
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verification Check
        # Logic:
        # 1. If user.is_verified is True -> Allow
        # 2. If user.is_verified is False AND verification_code is None -> Legacy User -> Allow
        # 3. If user.is_verified is False AND verification_code is NOT None -> New User Pending -> Block
        if not user.is_verified and user.verification_code is not None:
            raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

        # Set HttpOnly Cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.APP_MODE != "DEV",  # True for HTTPS in PROD
            samesite="none" if settings.APP_MODE != "DEV" else "lax",  # 'none' required for cross-origin
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Log successful login
        log = UserLog(
            user_id=user.id, event="LOGIN", details={}, ip_address=request.client.host if request.client else None
        )
        session.add(log)
        session.commit()

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_verified": user.is_verified,
                "verification_code": user.verification_code,
            },
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, 500
        # Critical error logged to file
        with open("error.log", "a") as f:
            f.write(f"CRITICAL ERROR IN LOGIN: {e}\n")
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Return current user information."""
    return {"email": user.email, "role": user.role}


@router.post("/google")
@limiter.limit("30/minute")
async def google_login(
    request: Request, response: Response, payload: GoogleLoginRequest, session: Session = Depends(get_session)
):
    """ """
    token = payload.credential
    client_id = settings.GOOGLE_CLIENT_ID

    if not client_id:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")

    try:
        # Try to verify as ID Token first (fast, local)
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
            email = idinfo["email"]
        except Exception:
            # Fallback: Treat as Access Token (fetch userinfo)
            import requests

            resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code != 200:
                raise ValueError("Invalid Access Token")

            user_info = resp.json()
            email = user_info.get("email")
            if not email:
                raise ValueError("Email not found in Google account")

        # Check if user exists
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            # Create new user automatically
            # New user created from Google OAuth
            user = User(
                email=email,
                hashed_password=get_password_hash(secrets.token_urlsafe(16)),  # Random password
                status="active",
                role="user",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # Create Access Token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

        # Set HttpOnly Cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.APP_MODE != "DEV",  # True for HTTPS in PROD
            samesite="none" if settings.APP_MODE != "DEV" else "lax",  # 'none' required for cross-origin
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Log successful login
        log = UserLog(
            user_id=user.id,
            event="LOGIN",
            details={"method": "google"},
            ip_address=request.client.host if request.client else None,
        )
        session.add(log)
        session.commit()

        return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.email, "role": user.role}}

    except ValueError:
        # Google token verification failed
        raise HTTPException(status_code=400, detail="Invalid Google Token")
    except Exception as e:
        # Error logged to error.log file
        import traceback

        traceback.print_exc()
        try:
            with open("error.log", "a") as f:
                f.write(f"CRITICAL ERROR IN GOOGLE LOGIN: {e}\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/forgot-password")
@limiter.limit("10/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    """
    Generates a reset token and sends it via email.
    """
    email = payload.email
    user = session.exec(select(User).where(User.email == email)).first()

    # Always return 200 to prevent email enumeration, unless specific need
    if not user:
        # Fake processing time?
        return {"message": "If email exists, a reset link has been sent."}

    # Generate Token
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
    session.add(user)
    session.commit()

    # Send Email in background
    background_tasks.add_task(send_reset_email, email, token)

    return {"message": "If email exists, a reset link has been sent."}


@router.post("/reset-password")
@limiter.limit("10/minute")
async def reset_password(request: Request, payload: ResetPasswordRequest, session: Session = Depends(get_session)):
    """
    Resets password using a valid token.
    """
    token = payload.token
    new_password = payload.new_password

    user = session.exec(select(User).where(User.reset_token == token)).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.reset_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    # Validate password strength
    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 10 caracteres, una mayúscula, una minúscula, un número y un carácter especial.",
        )

    # Update Password
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    # If they have access to email to reset password, they are verified
    user.is_verified = True
    user.verification_code = None
    session.add(user)
    session.commit()

    return {"message": "Password updated successfully"}
