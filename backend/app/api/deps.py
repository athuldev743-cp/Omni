from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import decode_token
from app.models import User, Tenant


reusable_oauth2 = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        return session
    raise RuntimeError("Failed to acquire DB session")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(reusable_oauth2),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_id = int(payload.get("sub", 0))
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_current_tenant(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> Tenant:
    stmt = select(Tenant).where(Tenant.id == current_user.tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentTenantDep = Annotated[Tenant, Depends(get_current_tenant)]

