from datetime import datetime
from typing import Any

from sqlalchemy import JSON, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Interaction(Base):
    lead_id: Mapped[int] = mapped_column(Integer, index=True)
    campaign_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel: Mapped[str] = mapped_column(String(50))  # email, whatsapp, voice
    status: Mapped[str] = mapped_column(String(50), default="pending")
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

