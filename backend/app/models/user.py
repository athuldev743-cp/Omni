from __future__ import annotations

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gmail_refresh_token_encrypted: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    meta_access_token_encrypted: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    meta_whatsapp_phone_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    meta_whatsapp_verify_token: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )

