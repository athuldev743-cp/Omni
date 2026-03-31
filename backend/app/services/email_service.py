from email.mime.text import MIMEText
import asyncio

import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import get_settings
from app.core.security import decrypt_token


settings = get_settings()


def _build_gmail_service(
    refresh_token_encrypted: str,
) -> any:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Google OAuth client is not configured")
    if not refresh_token_encrypted:
        raise RuntimeError("Missing encrypted Gmail refresh token")

    refresh_token = decrypt_token(refresh_token_encrypted)
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GMAIL_API_SCOPES,
    )
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    service = build("gmail", "v1", credentials=creds)
    return service


async def send_email_via_gmail(
    refresh_token_encrypted: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    def _send_sync() -> None:
        service = _build_gmail_service(refresh_token_encrypted)

        message = MIMEText(body)
        message["to"] = recipient
        message["from"] = sender
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        service.users().messages().send(userId="me", body=create_message).execute()

    await asyncio.to_thread(_send_sync)

