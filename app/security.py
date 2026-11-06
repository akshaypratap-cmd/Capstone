from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash

from app.config import settings


# Password hashing configuration
password_hash = PasswordHash.recommended()


# Hash password before saving
def hash_password(password: str):

    return password_hash.hash(password)


# Verify entered password
def verify_password(plain_password: str, hashed_password: str):

    return password_hash.verify(plain_password, hashed_password)


# Generate JWT access token
def create_access_token(user_id: int):

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


# Verify JWT token
def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        # Check whether user ID exists and is valid
        if not isinstance(user_id, str) or not user_id.isdecimal():
            return None

        user_id = int(user_id)

        if user_id <= 0:
            return None

        return user_id

    except (jwt.InvalidTokenError, ValueError, TypeError):

        return None