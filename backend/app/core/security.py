from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.models.token_blacklist import RevokedToken
from datetime import datetime
import uuid
import logging

logger = logging.getLogger("inventory.security")

# Password context: support pbkdf2_sha256 (default for new hashes), and
# also allow verifying existing argon2 and bcrypt hashes from older setups.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "argon2", "bcrypt"], deprecated="auto")

# OAuth2 scheme - tokenUrl points to our login endpoint (include API prefix)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_password(password: str) -> str:
    """Hash a password using the default scheme (pbkdf2_sha256)."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    # Add a unique token id (jti) for revocation tracking if not provided
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Log a short token snippet for debugging (do not log full token in production)
    try:
        token_snippet = (token[:50] + "...") if token and len(token) > 50 else token
    except Exception:
        token_snippet = "<unreadable>"
    logger.debug("get_current_user called with token snippet: %s", token_snippet)

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        logger.debug("Decoded token payload: %s", payload)
    except ExpiredSignatureError:
        logger.info("Token expired for token snippet: %s", token_snippet)
        raise credential_exception
    except JWTError as e:
        logger.info("JWT error decoding token (%s): %s", token_snippet, e)
        raise credential_exception

    user_id: str = payload.get("sub")
    jti: str = payload.get("jti")
    if user_id is None:
        raise credential_exception

    db = SessionLocal()
    # Check blacklist for this jti
    if jti:
        revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if revoked:
            db.close()
            logger.info("Rejected token because jti is revoked: %s", jti)
            raise credential_exception

    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except Exception as e:
        logger.exception("Error querying user id=%s: %s", user_id, e)
        db.close()
        raise credential_exception
    db.close()

    if user is None:
        logger.info("User not found for id=%s (token snippet=%s)", user_id, token_snippet)
        raise credential_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(allowed_roles: list):
    """Dependency factory to require one of the allowed roles."""
    def _require(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user

    return _require

# Convenience dependencies for common roles
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def require_client(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("client", "comprador", "user"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client privileges required")
    return current_user
