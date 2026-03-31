from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings


settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _derive_fernet_key_from_secret(secret_key: str) -> str:
    # Fernet expects a base64-encoded 32-byte key.
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8")


def _build_fernet() -> Fernet:
    # If FERNET_KEY is misconfigured (common in scaffolds), fall back deterministically
    # to a key derived from SECRET_KEY so the app can still start.
    try:
        return Fernet(settings.FERNET_KEY.encode("utf-8"))
    except Exception:
        derived = _derive_fernet_key_from_secret(settings.SECRET_KEY)
        return Fernet(derived.encode("utf-8"))


fernet = _build_fernet()


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    to_encode: dict[str, Any] = {"sub": subject}
    if extra_claims:
        to_encode.update(extra_claims)
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    try:
        return fernet.decrypt(token_encrypted.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted token") from exc

