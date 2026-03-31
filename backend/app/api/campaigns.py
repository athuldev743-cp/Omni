from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentTenantDep, DBSessionDep
from app.models import Campaign, Interaction, Lead, User
from app.schemas.common import (
    CampaignCreateRequest,
    CampaignOut,
    CampaignTriggerRequest,
)
from app.worker.tasks import (
    send_email_task,
    send_whatsapp_task,
    trigger_voice_call_task,
)


router = APIRouter()


@router.post("", response_model=CampaignOut)
async def create_campaign(
    payload: CampaignCreateRequest,
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> CampaignOut:
    if payload.channel not in {"email", "whatsapp", "voice"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel",
        )

    campaign = Campaign(
        tenant_id=tenant.id,
        name=payload.name,
        description=payload.description,
        channel=payload.channel,
    )
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    return campaign


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> list[CampaignOut]:
    result = await session.execute(
        select(Campaign).where(Campaign.tenant_id == tenant.id).order_by(Campaign.id.desc())
    )
    return list(result.scalars().all())


@router.post("/trigger")
async def trigger_campaign(
    payload: CampaignTriggerRequest,
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> dict:
    result = await session.execute(
        select(Campaign).where(
            Campaign.id == payload.campaign_id, Campaign.tenant_id == tenant.id
        )
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    result = await session.execute(
        select(Lead).where(Lead.id.in_(payload.lead_ids), Lead.tenant_id == tenant.id)
    )
    leads = result.scalars().all()
    if not leads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No leads to process",
        )

    owner = await session.execute(
        select(User).where(
            User.tenant_id == tenant.id,
        )
    )
    owner_user = owner.scalars().first()
    if owner_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant owner user not found",
        )

    queued = 0
    for lead in leads:
        interaction = Interaction(
            tenant_id=tenant.id,
            lead_id=lead.id,
            campaign_id=campaign.id,
            channel=campaign.channel,
            status="pending",
        )
        session.add(interaction)
        await session.flush()

        if campaign.channel == "email" and lead.email:
            if not owner_user.gmail_refresh_token_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gmail refresh token not connected for this tenant",
                )
            send_email_task.delay(
                tenant_id=tenant.id,
                interaction_id=interaction.id,
                refresh_token_encrypted=owner_user.gmail_refresh_token_encrypted,
                sender=owner_user.email,
                recipient=lead.email,
                subject=campaign.name,
                body=campaign.description or "",
            )
            queued += 1
        elif campaign.channel == "whatsapp" and lead.phone:
            if not owner_user.meta_access_token_encrypted or not owner_user.meta_whatsapp_phone_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Meta WhatsApp connection not configured for this tenant",
                )
            send_whatsapp_task.delay(
                tenant_id=tenant.id,
                interaction_id=interaction.id,
                to_phone=lead.phone,
                message=campaign.description or "",
                meta_access_token_encrypted=owner_user.meta_access_token_encrypted,
                meta_phone_id=owner_user.meta_whatsapp_phone_id,
            )
            queued += 1
        elif campaign.channel == "voice" and lead.phone:
            trigger_voice_call_task.delay(
                tenant_id=tenant.id,
                interaction_id=interaction.id,
                lead_id=lead.id,
                phone=lead.phone,
                expected_minutes=5,
            )
            queued += 1

    await session.commit()
    return {"queued": queued}

