from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tenant(Base):
    name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_info: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    products: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
    )

