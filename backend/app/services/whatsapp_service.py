from typing import Any, Optional

import re
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.security import decrypt_token
from app.models import Interaction, Lead, User
from app.services.ai_service import detect_intent_and_reply


E164_LIKE_RE = re.compile(r"^\+?\d{7,15}$")


def _looks_like_phone_number(identifier: str) -> bool:
    """
    True if the value is digits-only (optionally prefixed by '+').
    BSUIDs (e.g. `US.1a2b3c...`) will not match this.
    """
    return bool(E164_LIKE_RE.match(identifier.strip()))


def _extract_phone_number_from_text(text: str) -> str | None:
    """
    Best-effort extraction of a phone number from user message text.
    Expected to be E.164-like (e.g. +14155552671).
    """
    if not text:
        return None
    match = re.search(r"\+?\d{7,15}", text)
    if not match:
        return None
    candidate = match.group(0)
    return candidate if _looks_like_phone_number(candidate) else None


async def send_whatsapp_message(
    to_phone: str,
    message: str,
    meta_access_token_encrypted: str,
    meta_phone_id: str,
) -> None:
    if not meta_access_token_encrypted or not meta_phone_id:
        raise RuntimeError("Meta WhatsApp connection is not configured for this tenant")

    access_token = decrypt_token(meta_access_token_encrypted)

    url = f"https://graph.facebook.com/v20.0/{meta_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()


async def handle_whatsapp_webhook(
    data: dict[str, Any],
    session: AsyncSession,
) -> Optional[dict[str, Any]]:
    """
    Process WhatsApp webhook and enqueue AI auto-replies + (optional) voice calls.

    Multi-tenant routing is done by `phone_number_id` found in the webhook payload.
    """
    entry = (data.get("entry") or [{}])[0]
    changes = entry.get("changes") or []
    if not changes:
        return None

    value = changes[0].get("value", {})
    messages = value.get("messages") or []
    if not messages:
        return None

    message_obj = messages[0]
    from_phone = message_obj.get("from")
    text = message_obj.get("text", {}).get("body", "")

    phone_number_id = (
        value.get("metadata", {}) or {}
    ).get("phone_number_id")
    if not phone_number_id:
        return {"status": "ignored", "reason": "missing phone_number_id"}

    user_res = await session.execute(
        select(User).where(User.meta_whatsapp_phone_id == phone_number_id)
    )
    user = user_res.scalar_one_or_none()
    if user is None:
        return {"status": "ignored", "reason": "unknown phone_number_id"}

    tenant_id = user.tenant_id
    if not user.meta_access_token_encrypted:
        return {"status": "ignored", "reason": "missing meta access token"}

    from_identifier = (
        message_obj.get("wa_id")
        or message_obj.get("user_id")
        or from_phone
    )
    if not from_identifier:
        return {"status": "ignored", "reason": "missing from_identifier"}

    is_phone_identifier = _looks_like_phone_number(from_identifier)

    # Lookup by either the WhatsApp-scoped user identifier (BSUID/wa_id) or a
    # known digits-only phone number.
    lead_res = await session.execute(
        select(Lead).where(
            Lead.tenant_id == tenant_id,
            or_(
                Lead.whatsapp_uid == from_identifier,
                Lead.phone == from_identifier,
            ),
        )
    )
    lead = lead_res.scalar_one_or_none()
    if lead is None:
        lead_phone = from_identifier if is_phone_identifier else None
        lead = Lead(
            tenant_id=tenant_id,
            name=f"Lead {from_identifier}",
            email=None,
            phone=lead_phone,
            whatsapp_uid=from_identifier,
            source="whatsapp",
            ready_for_meet=False,
        )
        session.add(lead)
        await session.flush()

    ai_result = await detect_intent_and_reply(
        tenant_id=tenant_id,
        user_text=text or "",
        history=[{"role": "user", "content": text or ""}],
        sender_identifier=from_identifier,
    )
    intent = ai_result.get("intent") or "UNKNOWN"
    reply_text = ai_result.get("reply_text") or ""

    voice_phone: str | None = None
    ai_intent_wants_voice_call = intent == "READY_FOR_MEET"

    if ai_intent_wants_voice_call:
        # The user is ready, but we can only place a voice call when we have
        # a digits-only phone number.
        lead.ready_for_meet = True
        if is_phone_identifier:
            voice_phone = from_identifier
        else:
            # If the webhook identifier is a BSUID / username-scoped id, we
            # cannot place a voice call until we have a real digits-only phone.
            extracted_phone = _extract_phone_number_from_text(text or "")
            if extracted_phone:
                lead.phone = extracted_phone
                voice_phone = extracted_phone
            else:
                intent = "PHONE_NUMBER_REQUIRED"
                reply_text = (
                    "Thanks! To place the voice call, please reply with your "
                    "phone number (include country code, e.g., +14155552671)."
                )
    else:
        # If we previously captured "ready for meet" but still don't have a
        # digits-only phone, allow the next message (e.g., user replies with
        # their phone number) to complete the voice call trigger.
        if not is_phone_identifier and lead.ready_for_meet:
            extracted_phone = _extract_phone_number_from_text(text or "")
            if extracted_phone:
                lead.phone = extracted_phone
                voice_phone = extracted_phone
                intent = "READY_FOR_MEET"
                reply_text = "Perfect. We're placing your call now."

    session.add(lead)
    await session.flush()

    whatsapp_interaction = Interaction(
        tenant_id=tenant_id,
        lead_id=lead.id,
        campaign_id=None,
        channel="whatsapp",
        status="pending",
        payload={"message": reply_text, "intent": intent},
    )
    session.add(whatsapp_interaction)
    await session.flush()

    from app.worker.tasks import send_whatsapp_task, trigger_voice_call_task

    send_whatsapp_task.delay(
        tenant_id=tenant_id,
        interaction_id=whatsapp_interaction.id,
        to_phone=from_identifier,
        message=reply_text,
        meta_access_token_encrypted=user.meta_access_token_encrypted,
        meta_phone_id=user.meta_whatsapp_phone_id or phone_number_id,
    )

    voice_interaction_id: int | None = None
    if intent == "READY_FOR_MEET" and voice_phone:
        voice_interaction = Interaction(
            tenant_id=tenant_id,
            lead_id=lead.id,
            campaign_id=None,
            channel="voice",
            status="pending",
            payload={"expected_minutes": 5},
        )
        session.add(voice_interaction)
        await session.flush()
        voice_interaction_id = voice_interaction.id

        trigger_voice_call_task.delay(
            tenant_id=tenant_id,
            interaction_id=voice_interaction_id,
            lead_id=lead.id,
            phone=voice_phone,
            expected_minutes=5,
        )

    await session.commit()
    return {
        "status": "enqueued",
        "intent": intent,
        "lead_id": lead.id,
        "voice_interaction_id": voice_interaction_id,
    }

