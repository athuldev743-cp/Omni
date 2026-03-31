import asyncio
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Interaction, Lead, Tenant, User
from app.services import email_service, whatsapp_service, voice_service, billing_service
from app.services.ai_service import discover_leads


async def _get_session() -> AsyncSession:
    return AsyncSessionLocal()


async def _mark_interaction_started(session: AsyncSession, interaction_id: int) -> None:
    stmt = (
        update(Interaction)
        .where(Interaction.id == interaction_id)
        .values(started_at=datetime.now(timezone.utc))
    )
    await session.execute(stmt)
    await session.commit()


async def _update_interaction_status(
    session: AsyncSession,
    interaction_id: int,
    status: str,
    last_error: str | None = None,
    duration_minutes: int | None = None,
) -> None:
    stmt = (
        update(Interaction)
        .where(Interaction.id == interaction_id)
        .values(
            status=status,
            last_error=last_error,
            completed_at=datetime.now(timezone.utc),
            duration_minutes=duration_minutes,
        )
    )
    await session.execute(stmt)
    await session.commit()


@shared_task(name="lead_discovery_task")
def lead_discovery_task(tenant_id: int) -> None:
    async def run() -> None:
        session = await _get_session()
        try:
            # Enforce hard-stop wallet rule (<10 => stop) without spending credits.
            try:
                await billing_service.ensure_wallet_balance(session, tenant_id, 0)
            except billing_service.InsufficientCreditsError:
                return

            tenant = await session.get(Tenant, tenant_id)
            if tenant is None:
                return

            leads_data = await discover_leads(
                tenant_id=tenant_id,
                tone=tenant.tone,
                products=tenant.products,
                business_info=tenant.business_info,
                num_leads=10,
            )

            for lead_d in leads_data:
                email = lead_d.get("email")
                phone = lead_d.get("phone")

                existing_stmt = select(Lead).where(Lead.tenant_id == tenant_id)
                if email:
                    existing_stmt = existing_stmt.where(Lead.email == email)
                elif phone:
                    existing_stmt = existing_stmt.where(Lead.phone == phone)
                else:
                    # If we cannot uniquely identify a lead, skip creation.
                    continue

                existing_res = await session.execute(existing_stmt)
                existing = existing_res.scalar_one_or_none()

                if existing is None:
                    session.add(
                        Lead(
                            tenant_id=tenant_id,
                            name=lead_d.get("name") or "Unknown",
                            email=email,
                            phone=phone,
                            source=lead_d.get("source") or "discovery",
                            ready_for_meet=False,
                        )
                    )
                else:
                    existing.name = lead_d.get("name") or existing.name
                    existing.email = email or existing.email
                    existing.phone = phone or existing.phone
                    existing.source = lead_d.get("source") or existing.source

            await session.commit()
        except Exception as exc:  # noqa: BLE001
            # Discovery does not have a corresponding interaction record, so just fail fast.
            raise exc
        finally:
            await session.close()

    asyncio.run(run())


@shared_task(name="send_email_task")
def send_email_task(
    tenant_id: int,
    interaction_id: int,
    refresh_token_encrypted: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    async def run() -> None:
        session = await _get_session()
        try:
            await _mark_interaction_started(session, interaction_id)
            await billing_service.ensure_wallet_balance(
                session, tenant_id, billing_service.CHANNEL_COSTS["email"]
            )
            await email_service.send_email_via_gmail(
                refresh_token_encrypted, sender, recipient, subject, body
            )
            await billing_service.spend_credits(
                session, tenant_id, billing_service.CHANNEL_COSTS["email"]
            )
            await _update_interaction_status(session, interaction_id, "completed")
        except billing_service.InsufficientCreditsError as exc:
            await _update_interaction_status(
                session,
                interaction_id,
                "insufficient_funds",
                last_error=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            await _update_interaction_status(
                session, interaction_id, "failed", last_error=str(exc)
            )
        finally:
            await session.close()

    asyncio.run(run())


@shared_task(name="send_whatsapp_task")
def send_whatsapp_task(
    tenant_id: int,
    interaction_id: int,
    to_phone: str,
    message: str,
    meta_access_token_encrypted: str,
    meta_phone_id: str,
) -> None:
    async def run() -> None:
        session = await _get_session()
        try:
            await _mark_interaction_started(session, interaction_id)
            await billing_service.ensure_wallet_balance(
                session, tenant_id, billing_service.CHANNEL_COSTS["whatsapp"]
            )
            await whatsapp_service.send_whatsapp_message(
                to_phone=to_phone,
                message=message,
                meta_access_token_encrypted=meta_access_token_encrypted,
                meta_phone_id=meta_phone_id,
            )
            await billing_service.spend_credits(
                session, tenant_id, billing_service.CHANNEL_COSTS["whatsapp"]
            )
            await _update_interaction_status(session, interaction_id, "completed")
        except billing_service.InsufficientCreditsError as exc:
            await _update_interaction_status(
                session,
                interaction_id,
                "insufficient_funds",
                last_error=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            await _update_interaction_status(
                session, interaction_id, "failed", last_error=str(exc)
            )
        finally:
            await session.close()

    asyncio.run(run())


@shared_task(name="trigger_voice_call_task")
def trigger_voice_call_task(
    tenant_id: int,
    interaction_id: int,
    lead_id: int,
    phone: str,
    expected_minutes: int,
) -> None:
    async def run() -> None:
        session = await _get_session()
        try:
            await _mark_interaction_started(session, interaction_id)
            required = billing_service.CHANNEL_COSTS["voice"] * max(
                1, expected_minutes
            )
            await billing_service.ensure_wallet_balance(session, tenant_id, required)
            await voice_service.trigger_vapi_call(
                tenant_id=tenant_id,
                lead_id=lead_id,
                phone=phone,
                intent="READY_FOR_MEET",
            )
            await billing_service.spend_credits(session, tenant_id, required)
            await _update_interaction_status(
                session,
                interaction_id,
                "completed",
                duration_minutes=expected_minutes,
            )
        except billing_service.InsufficientCreditsError as exc:
            await _update_interaction_status(
                session,
                interaction_id,
                "insufficient_funds",
                last_error=str(exc),
                duration_minutes=expected_minutes,
            )
        except Exception as exc:  # noqa: BLE001
            await _update_interaction_status(
                session, interaction_id, "failed", last_error=str(exc)
            )
        finally:
            await session.close()

    asyncio.run(run())

