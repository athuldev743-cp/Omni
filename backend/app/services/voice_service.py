from typing import Any, Optional

import httpx

from app.core.config import get_settings


settings = get_settings()


async def trigger_vapi_call(
    tenant_id: int,
    lead_id: int,
    phone: str,
    intent: str,
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    """
    Trigger a Vapi.ai call for the given lead when the intent is READY_FOR_MEET.
    """
    if intent != "READY_FOR_MEET":
        raise RuntimeError("Voice call should only be triggered for READY_FOR_MEET")
    api_key = settings.VAPI_API_KEY
    if not api_key:
        raise RuntimeError("Vapi API key not configured")

    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "phoneNumber": phone,
        "metadata": {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
        },
    }
    if metadata:
        payload["metadata"].update(metadata)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

