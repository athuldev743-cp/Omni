from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings
from typing import List, Optional


FRONTEND_URL: str = "https://omni-flame-two.vercel.app"


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

    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE_SECONDS: int = 1800
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT_SECONDS: int = 30

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
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_CONFIG_ID: Optional[str] = None

    VAPI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Billing
    BILLING_WEBHOOK_SECRET: Optional[str] = None
    MIN_WALLET_CREDITS: int = 10

    # CORS / Frontend
    CORS_ORIGINS: List[AnyHttpUrl] = []
    FRONTEND_URL: str = "https://omni-flame-two.vercel.app"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def _normalized_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
        else:
            url = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]

        # Remove unsupported / unwanted params
        parsed = urlsplit(url)
        if parsed.query:
            REMOVE_KEYS = {"sslmode", "ssl", "channel_binding", "options"}
            query_pairs = [
                (k, v)
                for k, v in parse_qsl(parsed.query, keep_blank_values=True)
                if k not in REMOVE_KEYS
            ]
            url = urlunsplit(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    urlencode(query_pairs, doseq=True),
                    parsed.fragment,
                )
            )

        return url

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Backward-compatible alias (async)."""
        return self.sqlalchemy_database_uri_async

    @property
    def sqlalchemy_database_uri_sync(self) -> str:
        """Sync DB URL (for Alembic, scripts)."""
        url = self._normalized_database_url()
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    @property
    def sqlalchemy_database_uri_async(self) -> str:
        """Async DB URL (for app runtime)."""
        url = self._normalized_database_url()
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
