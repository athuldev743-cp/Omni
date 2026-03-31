from functools import lru_cache
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Core
    PROJECT_NAME: str = "OmniAgent SaaS"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = Field("super-secret-key-change-me", min_length=16)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"
    FERNET_KEY: str = Field(
        "0" * 44,
        description="Base64-encoded 32-byte key for Fernet; override via env",
    )

    COOKIE_NAME: str = "omniagent_token"

    # Database
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "omniagent"
    POSTGRES_USER: str = "omniagent"
    POSTGRES_PASSWORD: str = "omniagent"
    DATABASE_URL: Optional[str] = None

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # OAuth / Integrations
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[AnyHttpUrl] = None

    GMAIL_API_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    META_WHATSAPP_TOKEN: Optional[str] = None
    META_WHATSAPP_PHONE_ID: Optional[str] = None
    META_WHATSAPP_VERIFY_TOKEN: Optional[str] = None

    VAPI_API_KEY: Optional[str] = None

    GEMINI_API_KEY: Optional[str] = None

    # Billing
    BILLING_WEBHOOK_SECRET: Optional[str] = None
    MIN_WALLET_CREDITS: int = 10

    # CORS / Frontend
    CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        env_file_encoding = "utf-8"

    @property
    def sqlalchemy_database_uri(self) -> str:
        # Prefer explicit DATABASE_URL in hosted environments (e.g., Render).
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            # Render often provides postgres://...; SQLAlchemy expects postgresql://...
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://") :]
            # This app uses SQLAlchemy async engine with asyncpg.
            if url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

