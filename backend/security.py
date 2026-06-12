"""Seguridad serverless: hashing de contraseñas (bcrypt directo) y JWT (jose).

Se usa `bcrypt` directamente en vez de passlib (incompatible con bcrypt 4.x). bcrypt
trunca a 72 bytes: se trunca explícitamente para evitar errores.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from backend.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _encode(data: dict, expires: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires
    payload = {**data, "exp": expire, "type": token_type}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    return _encode(
        data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )


def create_refresh_token(data: dict) -> str:
    return _encode(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
