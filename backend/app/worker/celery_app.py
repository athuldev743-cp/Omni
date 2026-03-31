from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "omniagent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Ensure periodic retry scheduler is registered at worker startup.
from app.worker import scheduler  # noqa: E402,F401

