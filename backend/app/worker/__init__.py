from app.worker.celery_app import celery_app

# Import scheduler so periodic tasks are registered on worker startup.
from app.worker import scheduler  # noqa: F401,E402

