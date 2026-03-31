from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lead(Base):
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # WhatsApp "business scoped user id" (BSUID) / username-scoped identifier.
    # Example: `US.1a2b3c...` (may be alphanumeric + dots), up to 128 chars.
    whatsapp_uid: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ready_for_meet: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

