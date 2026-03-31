from fastapi import APIRouter

from . import auth, tenants, leads, campaigns, billing, whatsapp

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(
    whatsapp.router, prefix="/whatsapp", tags=["whatsapp-webhook"]
)

__all__ = ["api_router"]

