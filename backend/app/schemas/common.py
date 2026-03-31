from datetime import datetime
from typing import Optional

from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class TenantBase(BaseModel):
    name: str
    domain: Optional[str] = None
    tone: Optional[str] = None
    business_info: Optional[Dict[str, Any]] = None
    products: Optional[Dict[str, Any]] = None


class TenantCreate(TenantBase):
    initial_credits: int = 0


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    tone: Optional[str] = None
    business_info: Optional[Dict[str, Any]] = None
    products: Optional[Dict[str, Any]] = None


class TenantOut(TenantBase):
    id: int

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    tenant_id: int

    class Config:
        from_attributes = True


class LeadFilter(BaseModel):
    ready_for_meet: Optional[bool] = None
    source: Optional[str] = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    ready_for_meet: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignTriggerRequest(BaseModel):
    campaign_id: int
    lead_ids: list[int]


class WalletBalanceOut(BaseModel):
    tenant_id: int
    wallet_balance: int


class WalletTopupRequest(BaseModel):
    tenant_id: int
    credits: int


class MetaConnectRequest(BaseModel):
    meta_access_token: str
    meta_whatsapp_phone_id: str
    meta_whatsapp_verify_token: Optional[str] = None


class CampaignCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    channel: str  # email, whatsapp, voice


class CampaignOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    channel: str
    created_at: datetime

    class Config:
        from_attributes = True

