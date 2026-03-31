import asyncio
from datetime import datetime, timedelta, timezone

from celery.schedules import crontab
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Campaign, Interaction, Lead, User
from app.worker.celery_app import celery_app
from app.worker.tasks import (
    send_email_task,
    send_whatsapp_task,
    trigger_voice_call_task,
)


async def _get_session() -> AsyncSession:
    return AsyncSessionLocal()


async def _retry_failed_interactions() -> None:
    session = await _get_session()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=4)
        stmt = select(Interaction).where(
            Interaction.status == "failed",
            Interaction.completed_at <= cutoff,
        )
        result = await session.execute(stmt)
        interactions = result.scalars().all()

        for interaction in interactions:
            lead = await session.get(Lead, interaction.lead_id)
            if lead is None:
                await session.execute(
                    update(Interaction)
                    .where(Interaction.id == interaction.id)
                    .values(status="failed", last_error="Lead not found")
                )
                continue

            owner_user = (
                await session.execute(
                    select(User).where(User.tenant_id == interaction.tenant_id)
                )
            ).scalars().first()

            campaign = None
            if interaction.campaign_id is not None:
                campaign = await session.get(Campaign, interaction.campaign_id)

            await session.execute(
                update(Interaction)
                .where(Interaction.id == interaction.id)
                .values(status="pending", last_error=None)
            )

            if interaction.channel == "email":
                if owner_user is None or not owner_user.gmail_refresh_token_encrypted:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Gmail not connected")
                    )
                    continue
                if not lead.email:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Lead email missing")
                    )
                    continue

                subject = campaign.name if campaign else "Outreach"
                body = (campaign.description if campaign else "") or ""

                send_email_task.delay(
                    tenant_id=interaction.tenant_id,
                    interaction_id=interaction.id,
                    refresh_token_encrypted=owner_user.gmail_refresh_token_encrypted,
                    sender=owner_user.email,
                    recipient=lead.email,
                    subject=subject,
                    body=body,
                )

            elif interaction.channel == "whatsapp":
                if owner_user is None or not owner_user.meta_access_token_encrypted:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Meta not connected")
                    )
                    continue
                if not owner_user.meta_whatsapp_phone_id:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Meta WhatsApp phone_id missing")
                    )
                    continue
                if not lead.phone:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Lead phone missing")
                    )
                    continue

                message = None
                if campaign and campaign.description is not None:
                    message = campaign.description
                elif interaction.payload:
                    message = (interaction.payload.get("message") or None)  # type: ignore[union-attr]
                if not message:
                    message = ""

                send_whatsapp_task.delay(
                    tenant_id=interaction.tenant_id,
                    interaction_id=interaction.id,
                    to_phone=lead.phone,
                    message=message,
                    meta_access_token_encrypted=owner_user.meta_access_token_encrypted,
                    meta_phone_id=owner_user.meta_whatsapp_phone_id,
                )

            elif interaction.channel == "voice":
                if not lead.phone:
                    await session.execute(
                        update(Interaction)
                        .where(Interaction.id == interaction.id)
                        .values(status="failed", last_error="Lead phone missing")
                    )
                    continue

                expected_minutes = 5
                if interaction.payload and isinstance(interaction.payload, dict):
                    expected_minutes = int(interaction.payload.get("expected_minutes") or 5)

                trigger_voice_call_task.delay(
                    tenant_id=interaction.tenant_id,
                    interaction_id=interaction.id,
                    lead_id=interaction.lead_id,
                    phone=lead.phone,
                    expected_minutes=expected_minutes,
                )
            else:
                await session.execute(
                    update(Interaction)
                    .where(Interaction.id == interaction.id)
                    .values(status="failed", last_error=f"Unknown channel: {interaction.channel}")
                )

        await session.commit()
    finally:
        await session.close()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):  # type: ignore[override]
    # Run every hour to look for failed interactions older than 4 hours
    sender.add_periodic_task(
        crontab(minute=0, hour="*"),
        scan_and_retry_interactions.s(),  # type: ignore[arg-type]
        name="scan_failed_interactions_and_retry",
    )


@celery_app.task(name="scan_and_retry_interactions")
def scan_and_retry_interactions() -> None:
    """
    Periodic task that scans the DB for failed interactions older than 4 hours
    and enqueues retries.
    """
    asyncio.run(_retry_failed_interactions())

