from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from app.db.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserResponse, Token, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    oauth2_scheme
)
from app.models.token_blacklist import RevokedToken
from app.models.role import Role
from app.db.database import SessionLocal
from jose import jwt
from app.core.config import settings
import logging

logger = logging.getLogger("inventory.auth")

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Ensure default role exists
    default_role_name = "client"
    role_obj = db.query(Role).filter(Role.name == default_role_name).first()
    if not role_obj:
        role_obj = Role(name=default_role_name, description="Cliente/Comprador role")
        db.add(role_obj)
        db.commit()
        db.refresh(role_obj)

    # Create new user assigning the role name (denormalized string kept for compatibility)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        is_active=True,
        role=default_role_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Create access token with jti
    access_token_expires = timedelta(minutes=30)
    jti = str(uuid.uuid4())
    access_token = create_access_token(
        data={"sub": str(user.id), "jti": jti},
        expires_delta=access_token_expires
    )
    
    logger.info("User login success: %s (id=%s, jti=%s)", user.username, user.id, jti)

    return {"access_token": access_token, "token_type": "bearer"}

from datetime import datetime as _dt

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information. Return a plain dict compatible with `UserResponse` to avoid ORM serialization issues."""
    try:
        # Ensure `created_at` is a `datetime` for response validation.
        created_at_val = None
        try:
            if getattr(current_user, "created_at", None) is not None:
                if isinstance(current_user.created_at, _dt):
                    created_at_val = current_user.created_at
                else:
                    # Try to parse ISO string to datetime
                    try:
                        created_at_val = _dt.fromisoformat(str(current_user.created_at))
                    except Exception:
                        created_at_val = None
        except Exception:
            created_at_val = None

        data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "role": current_user.role,
            "created_at": created_at_val,
        }
        logger.debug("/me returned for user id=%s role=%s", current_user.id, current_user.role)
        # Construct Pydantic response model explicitly to catch validation errors early
        try:
            user_response = UserResponse(**data)
            return user_response
        except Exception as ve:
            logger.exception("UserResponse validation failed: %s", ve)
            raise HTTPException(status_code=500, detail=f"Response model validation error: {ve}")
    except Exception as e:
        logger.exception("Error serializing current_user for /me: %s", e)
        # Return the exception message in the response temporarily to aid debugging
        raise HTTPException(status_code=500, detail=f"Server error while returning user info: {e}")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint: revoke token by storing its jti in the blacklist"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
    except Exception:
        logger.info("Logout attempted with invalid/expired token")
        return JSONResponse({"message": "Invalid token or already expired"}, status_code=200)

    if not jti:
        logger.info("Logout token missing jti")
        return JSONResponse({"message": "Token has no jti; cannot revoke"}, status_code=200)

    db = SessionLocal()
    try:
        try:
            expires_at = datetime.fromtimestamp(int(exp)) if exp else None
        except Exception:
            expires_at = None

        existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if not existing:
            revoked = RevokedToken(jti=jti, expires_at=expires_at)
            db.add(revoked)
            db.commit()
            logger.info("Token revoked: jti=%s expires_at=%s", jti, expires_at)
        else:
            logger.debug("Token jti already revoked: %s", jti)
    except Exception:
        logger.exception("Error persisting revoked token jti=%s", jti)
    finally:
        db.close()

    return {"message": "Successfully logged out"}
