from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Wallet(Base):
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_wallet_tenant_id"),)

    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

