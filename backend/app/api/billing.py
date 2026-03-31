from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select, update

from app.api.deps import CurrentTenantDep, DBSessionDep
from app.schemas.common import WalletBalanceOut, WalletTopupRequest
from app.services.billing_service import get_wallet_balance
from app.core.config import get_settings
from app.models import Tenant, Wallet

import hashlib
import hmac


router = APIRouter()
settings = get_settings()


@router.get("/wallet", response_model=WalletBalanceOut)
async def get_wallet(
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> WalletBalanceOut:
    balance = await get_wallet_balance(session, tenant.id)
    return WalletBalanceOut(tenant_id=tenant.id, wallet_balance=balance)


@router.post("/webhook")
async def billing_webhook(
    request: Request,
    payload: WalletTopupRequest,
    session: DBSessionDep,
) -> dict:
    """
    Generic billing top-up webhook.\n
    Signature: HMAC-SHA256 over the raw request body with `BILLING_WEBHOOK_SECRET`.
    """
    secret = settings.BILLING_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing webhook secret not configured",
        )

    signature = request.headers.get("X-OmniAgent-Signature", "")
    raw_body = await request.body()
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    if payload.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="credits must be > 0",
        )

    tenant_exists = await session.execute(
        select(Tenant.id).where(Tenant.id == payload.tenant_id)
    )
    if tenant_exists.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    wallet_res = await session.execute(
        select(Wallet.id).where(Wallet.tenant_id == payload.tenant_id)
    )
    wallet_id = wallet_res.scalar_one_or_none()
    if wallet_id is None:
        session.add(Wallet(credits=payload.credits, tenant_id=payload.tenant_id))
        await session.commit()
    else:
        await session.execute(
            update(Wallet)
            .where(Wallet.tenant_id == payload.tenant_id)
            .values(credits=Wallet.credits + payload.credits)
        )
        await session.commit()

    balance = await get_wallet_balance(session, payload.tenant_id)
    return {"tenant_id": payload.tenant_id, "wallet_balance": balance}

