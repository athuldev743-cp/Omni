from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import get_settings
from app.models import Wallet

ChannelType = Literal["email", "whatsapp", "voice"]


CHANNEL_COSTS: dict[ChannelType, int] = {
    "email": 1,
    "whatsapp": 10,
    "voice": 100,  # per minute
}


class InsufficientCreditsError(Exception):
    pass


settings = get_settings()


async def get_wallet_balance(session: AsyncSession, tenant_id: int) -> int:
    result = await session.execute(
        select(Wallet.credits).where(Wallet.tenant_id == tenant_id)
    )
    balance = result.scalar_one_or_none()
    return int(balance or 0)


async def ensure_wallet_balance(
    session: AsyncSession,
    tenant_id: int,
    required_credits: int,
) -> None:
    # Hard stop rule: no action allowed if wallet has fewer than 10 credits.
    balance = await get_wallet_balance(session, tenant_id)
    if balance < settings.MIN_WALLET_CREDITS:
        raise InsufficientCreditsError(
            f"Wallet below minimum credits: required_min={settings.MIN_WALLET_CREDITS}, balance={balance}"
        )
    if balance < required_credits:
        raise InsufficientCreditsError(
            f"Insufficient credits: required={required_credits}, balance={balance}"
        )


async def spend_credits(
    session: AsyncSession,
    tenant_id: int,
    amount: int,
) -> None:
    if amount <= 0:
        return
    await ensure_wallet_balance(session, tenant_id, amount)
    stmt = (
        update(Wallet)
        .where(Wallet.tenant_id == tenant_id)
        .values(credits=Wallet.credits - amount)
    )
    await session.execute(stmt)
    await session.commit()

