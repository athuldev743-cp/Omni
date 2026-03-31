from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentTenantDep, DBSessionDep
from app.models import Tenant
from app.models import Wallet
from app.schemas.common import TenantCreate, TenantUpdate, TenantOut


router = APIRouter()


@router.get("/me", response_model=TenantOut)
async def get_my_tenant(current_tenant: CurrentTenantDep) -> TenantOut:
    return current_tenant


@router.post("/", response_model=TenantOut)
async def create_tenant(
    payload: TenantCreate,
    session: DBSessionDep,
) -> TenantOut:
    tenant = Tenant(
        name=payload.name,
        domain=payload.domain,
        tone=payload.tone,
        business_info=payload.business_info,
        products=payload.products,
        tenant_id=0,
    )
    session.add(tenant)
    await session.flush()
    tenant.tenant_id = tenant.id

    wallet = Wallet(credits=payload.initial_credits, tenant_id=tenant.id)
    session.add(wallet)
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantOut)
async def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    session: DBSessionDep,
) -> TenantOut:
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    if payload.name is not None:
        tenant.name = payload.name
    if payload.domain is not None:
        tenant.domain = payload.domain
    if payload.tone is not None:
        tenant.tone = payload.tone
    if payload.business_info is not None:
        tenant.business_info = payload.business_info
    if payload.products is not None:
        tenant.products = payload.products
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.patch("/me", response_model=TenantOut)
async def update_my_tenant(
    payload: TenantUpdate,
    current_tenant: CurrentTenantDep,
    session: DBSessionDep,
) -> TenantOut:
    tenant = await session.get(Tenant, current_tenant.id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    if payload.name is not None:
        tenant.name = payload.name
    if payload.domain is not None:
        tenant.domain = payload.domain
    if payload.tone is not None:
        tenant.tone = payload.tone
    if payload.business_info is not None:
        tenant.business_info = payload.business_info
    if payload.products is not None:
        tenant.products = payload.products

    await session.commit()
    await session.refresh(tenant)
    return tenant

