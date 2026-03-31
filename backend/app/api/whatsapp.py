from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from app import settings
from app.api.deps import DBSessionDep
from app.models import User
from app.services.whatsapp_service import handle_whatsapp_webhook

router = APIRouter()


@router.get("/webhook")   # ✅ was "/verify" — Meta calls /webhook
async def verify_webhook(
    request: Request,
    session: DBSessionDep,
) -> Response:
    mode         = request.query_params.get("hub.mode")
    challenge    = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    if mode != "subscribe" or not challenge or not verify_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification failed",
        )

    # Single-tenant: match against env var
    if (
        settings.META_WHATSAPP_VERIFY_TOKEN
        and verify_token == settings.META_WHATSAPP_VERIFY_TOKEN
    ):
        return Response(content=challenge, media_type="text/plain")  # ✅ plain text

    # Multi-tenant: look up token in DB
    user_res = await session.execute(
        select(User).where(User.meta_whatsapp_verify_token == verify_token)
    )
    user = user_res.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification failed",
        )

    return Response(content=challenge, media_type="text/plain")  # ✅ plain text


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    session: DBSessionDep,
) -> dict:
    payload = await request.json()
    result  = await handle_whatsapp_webhook(payload, session=session)
    return {"status": "ok", "result": result}
