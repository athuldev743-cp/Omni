from datetime import datetime
import json
import random
import re
from typing import Any

import httpx

from app.core.config import get_settings


settings = get_settings()

DIALABLE_PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def is_dialable_phone_number(identifier: str | None) -> bool:
    """
    Return True when `identifier` looks like a real dialable phone number
    (digits-only, optional leading '+').

    This intentionally returns False for WhatsApp username / BSUID identifiers
    like `US.1a2b3c...`.
    """
    if not identifier:
        return False
    return bool(DIALABLE_PHONE_RE.match(identifier.strip()))


async def summarize_chat_history(
    messages: list[dict[str, Any]],
    tenant_id: int,
) -> str:
    """
    Call Gemini 1.5 Flash (or compatible) to summarize chat history.
    The implementation assumes a generic HTTP API compatible with Gemini-style calls.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        # Fallback: simple heuristic summary
        last_messages = messages[-5:]
        joined = " ".join(m.get("content", "") for m in last_messages)
        return f"[Local summary for tenant {tenant_id} at {datetime.utcnow().isoformat()}]: {joined[:500]}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Summarize the following chat history focusing on lead intent and readiness for a meeting:\n"
                        + "\n".join(
                            f"{m.get('role','user')}: {m.get('content','')}"
                            for m in messages
                        )
                    }
                ],
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            params={"key": api_key},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return "No summary available."
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return "No summary available."
        return str(parts[0].get("text") or "No summary available.")


async def detect_intent_and_reply(
    tenant_id: int,
    user_text: str,
    history: list[dict[str, Any]] | None = None,
    sender_identifier: str | None = None,
) -> dict[str, str]:
    """
    Detect WhatsApp intent and generate an AI reply.

    Intent contract:
    - READY_FOR_MEET
    - OTHER
    """
    history = history or [{"role": "user", "content": user_text}]
    summary = await summarize_chat_history(history, tenant_id=tenant_id)

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        text = (user_text or "").lower()
        ready_keywords = ["yes", "book", "schedule", "call", "meet", "tomorrow", "today"]
        is_ready = any(k in text for k in ready_keywords)
        intent = "READY_FOR_MEET" if is_ready else "OTHER"
        if intent == "READY_FOR_MEET":
            if not is_dialable_phone_number(sender_identifier):
                return {
                    "intent": "PHONE_NUMBER_REQUIRED",
                    "reply_text": "Thanks! Please reply with your phone number (include country code, e.g., +14155552671) so we can place the call.",
                }
            return {
                "intent": intent,
                "reply_text": "Great. What day and time works best for you? Reply with a preferred time slot (e.g., “Tomorrow 3 PM”).",
            }
        return {
            "intent": intent,
            "reply_text": "Thanks for reaching out. Tell me a bit about your goal and I will suggest the next steps. If you want to book a quick meet, reply YES.",
        }

    dialable_hint = (
        "We have the user's dialable phone number on file."
        if is_dialable_phone_number(sender_identifier)
        else "The user is contacting via a WhatsApp username/BSUID, so we may NOT have a dialable phone number yet."
    )
    prompt = (
        "You are an outreach assistant for a multi-tenant SaaS.\n"
        "A tenant-specific lead just messaged you on WhatsApp.\n\n"
        f"Sender identifier context:\n{dialable_hint}\n\n"
        f"Tenant summary (chat memory buffer):\n{summary}\n\n"
        f"Latest message:\n{user_text}\n\n"
        "Task:\n"
        "- Classify the user's intent into either READY_FOR_MEET or OTHER.\n"
        "- Produce a concise, friendly WhatsApp reply to the user.\n\n"
        "Rules:\n"
        "- If the user is ready/wants to book/schedule a meeting, set intent to READY_FOR_MEET.\n"
        "- If the user is ready for a voice call but we do NOT have a dialable phone number yet, ask them to share their phone number (with country code) instead of implying we will call immediately.\n"
        "- Otherwise intent is OTHER.\n"
        "- Reply text must be short (max 2-4 sentences).\n"
        "- Output ONLY a valid JSON object with keys: intent, reply_text.\n"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            params={"key": api_key},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    raw_text = (
        data.get("candidates") or [{}]
    )[0].get("content", {}).get("parts", [{}])[0].get("text") or ""

    try:
        parsed = json.loads(raw_text)
        intent = parsed.get("intent") or "OTHER"
        reply_text = parsed.get("reply_text") or ""
        return {"intent": intent, "reply_text": reply_text}
    except Exception:
        # Try to salvage JSON from within a larger string.
        match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
        if not match:
            return {"intent": "OTHER", "reply_text": "Thanks for reaching out. How can I help?"}
        parsed = json.loads(match.group(0))
        intent = parsed.get("intent") or "OTHER"
        reply_text = parsed.get("reply_text") or ""
        return {"intent": intent, "reply_text": reply_text}


async def discover_leads(
    tenant_id: int,
    tone: str | None,
    products: dict[str, Any] | None,
    business_info: dict[str, Any] | None,
    num_leads: int = 10,
) -> list[dict[str, Any]]:
    """
    Generate lead candidates for a tenant.

    Returns list items with: name, email, phone, source.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        # Deterministic fallback lead generator (no external dependencies).
        random.seed(tenant_id + (len(tone or "") * 31) + (len((products or {})) * 17))
        first_names = [
            "Aarav",
            "Maya",
            "Noah",
            "Aisha",
            "Ethan",
            "Zara",
            "Liam",
            "Ivy",
            "Lucas",
            "Nora",
            "Arjun",
            "Sara",
        ]
        last_names = ["Patel", "Sharma", "Khan", "Singh", "Garcia", "Kim", "Brown", "Nguyen"]
        sources = ["discovery", "product_interest", "web_search"]

        leads: list[dict[str, Any]] = []
        for i in range(num_leads):
            fn = first_names[(i * 3) % len(first_names)]
            ln = last_names[(i * 5) % len(last_names)]
            name = f"{fn} {ln}"
            local = f"{fn}.{ln}".lower().replace(" ", "")
            email = f"{local}{tenant_id}@example.com"
            phone = f"+1555{(tenant_id * 97 + i * 13) % 100000000:08d}"
            leads.append({"name": name, "email": email, "phone": phone, "source": random.choice(sources)})
        return leads

    products_text = json.dumps(products or {}, ensure_ascii=False)
    business_info_text = json.dumps(business_info or {}, ensure_ascii=False)
    tone_text = tone or ""

    prompt = (
        "You are generating outbound lead targets for a multi-tenant SaaS.\n"
        f"Tenant tone: {tone_text}\n"
        f"Products JSON: {products_text}\n"
        f"Business info JSON: {business_info_text}\n\n"
        f"Generate exactly {num_leads} lead candidates.\n"
        "Each lead must include:\n"
        "- name (string)\n"
        "- email (string, can be example.com)\n"
        "- phone (string in E.164 format, can be +1555...) \n"
        "- source (string describing why we chose this lead)\n\n"
        "Output ONLY a valid JSON array of objects. No markdown."
    )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            params={"key": api_key},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    raw_text = (
        data.get("candidates") or [{}]
    )[0].get("content", {}).get("parts", [{}])[0].get("text") or ""

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # Fallback if parsing fails (deterministic generator).
    random.seed(tenant_id + (len(tone or "") * 31) + (len((products or {})) * 17))
    first_names = [
        "Aarav",
        "Maya",
        "Noah",
        "Aisha",
        "Ethan",
        "Zara",
        "Liam",
        "Ivy",
        "Lucas",
        "Nora",
        "Arjun",
        "Sara",
    ]
    last_names = ["Patel", "Sharma", "Khan", "Singh", "Garcia", "Kim", "Brown", "Nguyen"]
    sources = ["discovery", "product_interest", "web_search"]

    leads: list[dict[str, Any]] = []
    for i in range(num_leads):
        fn = first_names[(i * 3) % len(first_names)]
        ln = last_names[(i * 5) % len(last_names)]
        name = f"{fn} {ln}"
        local = f"{fn}.{ln}".lower().replace(" ", "")
        email = f"{local}{tenant_id}@example.com"
        phone = f"+1555{(tenant_id * 97 + i * 13) % 100000000:08d}"
        leads.append(
            {"name": name, "email": email, "phone": phone, "source": random.choice(sources)}
        )
    return leads

