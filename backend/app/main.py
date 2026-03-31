from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import settings
from app.api import api_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


# ✅ app must be created BEFORE middleware/routes
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/health")
async def api_health() -> dict:
    return {"status": "ok"}


@app.middleware("http")
async def inject_user_from_cookie(request: Request, call_next):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token and "authorization" not in request.headers:
        request.scope["headers"] = list(request.scope["headers"]) + [
            (b"authorization", f"Bearer {token}".encode())
        ]
    response = await call_next(request)
    return response


app.include_router(api_router, prefix=settings.API_V1_PREFIX)