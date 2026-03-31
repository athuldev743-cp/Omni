from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.api.deps import DBSessionDep, CurrentUserDep
from app.core.security import create_access_token, encrypt_token
from app.models import Tenant, User, Wallet
from app.schemas.common import MetaConnectRequest


router = APIRouter()


@router.get("/google/login")
async def google_login() -> Response:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth is not configured.",
        )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": str(settings.GOOGLE_REDIRECT_URI),
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{query}"
    return RedirectResponse(url)


async def _exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    # Minimal manual OAuth2 exchange to avoid extra dependencies
    import httpx

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth is not configured.",
        )
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": str(settings.GOOGLE_REDIRECT_URI),
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data=data)
        resp.raise_for_status()
        return resp.json()


async def _fetch_userinfo(access_token: str) -> Dict[str, Any]:
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    session: DBSessionDep,
) -> Response:
    code: Optional[str] = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code")

    token_data = await _exchange_code_for_tokens(code)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to obtain access token",
        )

    userinfo = await _fetch_userinfo(access_token)
    email = userinfo.get("email")
    sub = userinfo.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to obtain user email",
        )

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        tenant = Tenant(
            name=f"{email} Tenant",
            domain=None,
            tone=None,
            business_info=None,
            products=None,
            tenant_id=0,
        )
        session.add(tenant)
        await session.flush()

        tenant.tenant_id = tenant.id
        user = User(
            email=email,
            hashed_password="",
            is_active=True,
            is_superuser=False,
            google_sub=sub,
            tenant_id=tenant.id,
        )
        session.add(Wallet(credits=0, tenant_id=tenant.id))
        if refresh_token:
            user.gmail_refresh_token_encrypted = encrypt_token(refresh_token)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        if refresh_token:
            user.gmail_refresh_token_encrypted = encrypt_token(refresh_token)
        await session.commit()

    wallet_exists = await session.execute(
        select(Wallet.id).where(Wallet.tenant_id == user.tenant_id)
    )
    if wallet_exists.scalar_one_or_none() is None:
        session.add(Wallet(credits=0, tenant_id=user.tenant_id))
        await session.commit()

    jwt_token = create_access_token(str(user.id), extra_claims={"tenant_id": user.tenant_id})
    response = RedirectResponse(url="/")
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=jwt_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


@router.get("/me")
async def read_me(current_user: CurrentUserDep) -> Dict[str, Any]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active,
    }


@router.post("/meta/connect")
async def connect_meta(
    payload: MetaConnectRequest,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> dict:
    user_res = await session.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.meta_access_token_encrypted = encrypt_token(payload.meta_access_token)
    user.meta_whatsapp_phone_id = payload.meta_whatsapp_phone_id
    user.meta_whatsapp_verify_token = payload.meta_whatsapp_verify_token
    await session.commit()

    return {
        "status": "connected",
        "tenant_id": user.tenant_id,
        "meta_whatsapp_phone_id": user.meta_whatsapp_phone_id,
    }

