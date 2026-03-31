from typing import List

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentTenantDep, DBSessionDep
from app.models import Lead
from app.schemas.common import LeadFilter, LeadOut


router = APIRouter()


@router.get("/ready_for_meet", response_model=List[LeadOut])
async def list_ready_for_meet(
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> list[LeadOut]:
    stmt = select(Lead).where(
        Lead.tenant_id == tenant.id,
        Lead.ready_for_meet.is_(True),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/filter", response_model=List[LeadOut])
async def filter_leads(
    filters: LeadFilter,
    tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> list[LeadOut]:
    stmt = select(Lead).where(Lead.tenant_id == tenant.id)
    if filters.ready_for_meet is not None:
        stmt = stmt.where(Lead.ready_for_meet == filters.ready_for_meet)
    if filters.source is not None:
        stmt = stmt.where(Lead.source == filters.source)
    result = await session.execute(stmt)
    leads = result.scalars().all()
    return list(leads)

