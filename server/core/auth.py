"""
Authentication and security system for the auction system.
Handles JWT tokens, password hashing, user authentication, and security features.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from core.redis_manager import redis_manager
from db.database import get_db
from models.auction import User, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class AuthManager:
    """Authentication manager for handling user authentication and authorization."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    async def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            if not user.is_active:
                return None

            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()

            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Get current authenticated user from JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            token = credentials.credentials
            payload = self.verify_token(token)

            if payload is None:
                raise credentials_exception

            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception

            # Check if token is blacklisted
            if await self.is_token_blacklisted(token):
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """Get current active user."""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user

    def check_permissions(self, user: User, required_roles: list) -> bool:
        """Check if user has required permissions."""
        return user.role in required_roles

    async def require_roles(self, required_roles: list):
        """Dependency to require specific user roles."""
        def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
            if not self.check_permissions(current_user, required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return role_checker

    async def blacklist_token(self, token: str, expires_in: int = 3600) -> bool:
        """Add token to blacklist."""
        try:
            key = f"blacklist:{token}"
            return await redis_manager.set_cache(key, {"blacklisted": True}, expires_in)
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        try:
            key = f"blacklist:{token}"
            return await redis_manager.get_cache(key) is not None
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False

    async def create_user_session(self, user: User) -> dict:
        """Create user session with tokens."""
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=self.refresh_token_expire_days)

        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )

        refresh_token = self.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Store session in Redis
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "created_at": datetime.utcnow().isoformat(),
            "refresh_token": refresh_token
        }

        session_id = f"session:{user.id}:{datetime.utcnow().timestamp()}"
        await redis_manager.set_session(session_id, session_data, 3600)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "session_id": session_id
        }

    async def refresh_access_token(self, refresh_token: str, db: Session) -> Optional[dict]:
        """Refresh access token using refresh token."""
        try:
            payload = self.verify_token(refresh_token)
            if payload is None or payload.get("type") != "refresh":
                return None

            user_id = int(payload.get("sub"))
            user = db.query(User).filter(User.id == user_id).first()

            if not user or not user.is_active:
                return None

            # Create new access token
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role.value},
                expires_delta=access_token_expires
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    async def logout(self, token: str) -> bool:
        """Logout user by blacklisting token."""
        try:
            # Blacklist the token
            await self.blacklist_token(token, 3600)

            # Clear user session
            payload = self.verify_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    await redis_manager.clear_pattern(f"session:{user_id}:*")

            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False


# Global auth manager instance
auth_manager = AuthManager()


# Dependency functions for FastAPI
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    return auth_manager.get_current_user(credentials, db)


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    return auth_manager.get_current_active_user(current_user)


def require_roles(required_roles: list):
    """Dependency to require specific user roles."""
    return auth_manager.require_roles(required_roles)


# Role-based access control
require_admin = require_roles([UserRole.ADMIN])
require_moderator = require_roles([UserRole.ADMIN, UserRole.MODERATOR])
require_seller = require_roles([UserRole.SELLER, UserRole.ADMIN, UserRole.MODERATOR])
require_buyer = require_roles([UserRole.BUYER, UserRole.SELLER, UserRole.ADMIN, UserRole.MODERATOR])


# Rate limiting decorator
async def rate_limit(key: str, max_requests: int = 100, window: int = 3600):
    """Rate limiting dependency."""
    async def rate_limiter():
        allowed = await redis_manager.check_rate_limit(key, max_requests, window)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
    return rate_limiter


# Security utilities
def validate_password_strength(password: str) -> dict:
    """Validate password strength."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    import html

    # HTML escape
    sanitized = html.escape(text)

    # Remove potentially dangerous characters
    dangerous_chars = ['<script>', '</script>', 'javascript:', 'onload=', 'onerror=']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char.lower(), '')

    return sanitized


# Audit logging
async def log_audit_event(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """Log audit event."""
    try:
        from models.auction import AuditLog
        import json

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(audit_log)
        db.commit()

    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        db.rollback()