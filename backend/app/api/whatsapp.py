from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select
import httpx

from app import settings
from app.api.deps import DBSessionDep, CurrentUserDep
from app.core.security import encrypt_token
from app.models import User
from app.services.whatsapp_service import handle_whatsapp_webhook

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request, session: DBSessionDep) -> Response:
    mode         = request.query_params.get("hub.mode")
    challenge    = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    if mode != "subscribe" or not challenge or not verify_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

    if settings.META_WHATSAPP_VERIFY_TOKEN and verify_token == settings.META_WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    user_res = await session.execute(select(User).where(User.meta_whatsapp_verify_token == verify_token))
    user = user_res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

    return Response(content=challenge, media_type="text/plain")


@router.post("/webhook")
async def whatsapp_webhook(request: Request, session: DBSessionDep) -> dict:
    payload = await request.json()
    result  = await handle_whatsapp_webhook(payload, session=session)
    return {"status": "ok", "result": result}


@router.post("/onboard")
async def onboard_whatsapp(
    request: Request,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> dict:
    """
    Receives the 'code' from Meta Embedded Signup popup.
    Exchanges it for a long-lived token, fetches WABA_ID + PHONE_NUMBER_ID,
    and saves everything to the user's record.
    """
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Meta App credentials not configured on server",
        )

    body = await request.json()
    code = body.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code")

    async with httpx.AsyncClient(timeout=30.0) as client:

        # ── Step 1: Exchange code → short-lived user access token ──────────
        token_res = await client.get(
            "https://graph.facebook.com/v21.0/oauth/access_token",
            params={
                "client_id":     settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "code":          code,
            },
        )
        token_res.raise_for_status()
        token_data       = token_res.json()
        short_lived_token = token_data.get("access_token")
        if not short_lived_token:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_data}")

        # ── Step 2: Exchange short-lived → long-lived token ─────────────────
        long_lived_res = await client.get(
            "https://graph.facebook.com/v21.0/oauth/access_token",
            params={
                "grant_type":        "fb_exchange_token",
                "client_id":         settings.META_APP_ID,
                "client_secret":     settings.META_APP_SECRET,
                "fb_exchange_token": short_lived_token,
            },
        )
        long_lived_res.raise_for_status()
        long_lived_token = long_lived_res.json().get("access_token") or short_lived_token

        # ── Step 3: Fetch WABA_ID and PHONE_NUMBER_ID from Graph API ────────
        waba_res = await client.get(
            "https://graph.facebook.com/v21.0/me/businesses",
            params={"access_token": long_lived_token, "fields": "whatsapp_business_accounts"},
        )
        waba_res.raise_for_status()
        waba_data = waba_res.json()

        waba_id       = None
        phone_number_id = None

        businesses = waba_data.get("data") or []
        for biz in businesses:
            waba_accounts = biz.get("whatsapp_business_accounts", {}).get("data") or []
            if waba_accounts:
                waba_id = waba_accounts[0].get("id")
                break

        if waba_id:
            phones_res = await client.get(
                f"https://graph.facebook.com/v21.0/{waba_id}/phone_numbers",
                params={"access_token": long_lived_token},
            )
            if phones_res.status_code == 200:
                phones_data = phones_res.json().get("data") or []
                if phones_data:
                    phone_number_id = phones_data[0].get("id")

    # ── Step 4: Save to DB ───────────────────────────────────────────────────
    user_res = await session.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.meta_access_token_encrypted = encrypt_token(long_lived_token)
    user.meta_waba_id                = waba_id
    user.meta_whatsapp_phone_id      = phone_number_id

    await session.commit()

    return {
        "status":          "connected",
        "waba_id":         waba_id,
        "phone_number_id": phone_number_id,
    }