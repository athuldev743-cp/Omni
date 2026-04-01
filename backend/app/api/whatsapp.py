from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select
import httpx

from app import settings
from app.api.deps import DBSessionDep, CurrentUserDep
from app.core.security import encrypt_token
from app.models import User
from app.services.whatsapp_service import handle_whatsapp_webhook

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# WEBHOOK VERIFICATION
# ─────────────────────────────────────────────────────────────
@router.get("/webhook")
async def verify_webhook(request: Request, session: DBSessionDep) -> Response:
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    if mode != "subscribe" or not challenge or not verify_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification failed"
        )

    # Global verify token
    if settings.META_WHATSAPP_VERIFY_TOKEN and verify_token == settings.META_WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    # User-specific token
    user_res = await session.execute(
        select(User).where(User.meta_whatsapp_verify_token == verify_token)
    )
    user = user_res.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification failed"
        )

    return Response(content=challenge, media_type="text/plain")


# ─────────────────────────────────────────────────────────────
# WEBHOOK RECEIVER
# ─────────────────────────────────────────────────────────────
@router.post("/webhook")
async def whatsapp_webhook(request: Request, session: DBSessionDep) -> dict:
    payload = await request.json()
    result = await handle_whatsapp_webhook(payload, session=session)
    return {"status": "ok", "result": result}


# ─────────────────────────────────────────────────────────────
# ONBOARD WHATSAPP (FIXED)
# ─────────────────────────────────────────────────────────────
@router.post("/onboard")
async def onboard_whatsapp(
    request: Request,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> dict:

    # ── Validate config ──────────────────────────────────────
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Meta App credentials not configured"
        )

    body = await request.json()
    short_lived_token = body.get("access_token")

    if not short_lived_token:
        raise HTTPException(status_code=400, detail="Missing access_token")

    async with httpx.AsyncClient(timeout=30.0) as client:

        # ── Step 1: Exchange token ────────────────────────────
        long_lived_res = await client.get(
            "https://graph.facebook.com/v21.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "fb_exchange_token": short_lived_token,
            },
        )

        if not long_lived_res.is_success:
            raise HTTPException(
                status_code=502,
                detail=f"Token exchange failed: {long_lived_res.text}",
            )

        long_lived_token = (
            long_lived_res.json().get("access_token")
            or short_lived_token
        )

        print("LONG TOKEN:", long_lived_token)

        # ── Step 2: Fetch WABA (PRIMARY METHOD) ───────────────
        waba_id = None
        phone_number_id = None

        waba_res = await client.get(
            "https://graph.facebook.com/v21.0/me/whatsapp_business_accounts",
            params={"access_token": long_lived_token},
        )

        print("WABA DIRECT:", waba_res.text)

        if waba_res.is_success:
            accounts = waba_res.json().get("data") or []
            if accounts:
                waba_id = accounts[0].get("id")

        # ── Step 2B: Fallback ─────────────────────────────────
        if not waba_id:
            fallback_res = await client.get(
                "https://graph.facebook.com/v21.0/me",
                params={
                    "access_token": long_lived_token,
                    "fields": "whatsapp_business_accounts",
                },
            )

            print("WABA FALLBACK:", fallback_res.text)

            if fallback_res.is_success:
                accounts = (
                    fallback_res.json()
                    .get("whatsapp_business_accounts", {})
                    .get("data") or []
                )
                if accounts:
                    waba_id = accounts[0].get("id")

        # ── HARD FAIL if still missing ────────────────────────
        if not waba_id:
            raise HTTPException(
                status_code=400,
                detail="No WhatsApp Business Account found. Check token permissions.",
            )

        # ── Step 3: Fetch Phone Number ID ─────────────────────
        phones_res = await client.get(
            f"https://graph.facebook.com/v21.0/{waba_id}/phone_numbers",
            params={"access_token": long_lived_token},
        )

        print("PHONES:", phones_res.text)

        if phones_res.is_success:
            phones = phones_res.json().get("data") or []
            if phones:
                phone_number_id = phones[0].get("id")

    # ── Step 4: Save to DB ───────────────────────────────────
    user_res = await session.execute(
        select(User).where(User.id == current_user.id)
    )
    user = user_res.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.meta_access_token_encrypted = encrypt_token(long_lived_token)
    user.meta_waba_id = waba_id
    user.meta_whatsapp_phone_id = phone_number_id

    await session.commit()

    return {
        "status": "connected",
        "waba_id": waba_id,
        "phone_number_id": phone_number_id,
    }