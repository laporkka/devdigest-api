from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


BROKER_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
BACKEND_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1"


celery_app = Celery(
    "devdigest_tasks",
    broker=BROKER_URL,
    backend=BACKEND_URL
)


celery_app.conf.update(
    task_serializer="json",       
    accept_content=["json"],      
    result_serializer="json",     
    timezone="UTC",               
    enable_utc=True,
    task_track_started=True
)


celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.imports = ("app.tasks.parsers",)

celery_app.conf.beat_schedule = {
    "parse-hn-every-hour": {
        "task": "tasks.parse_hackernews",  
        "schedule": crontab(minute=0),     
    },
}

celery_app.conf.timezone = "UTC"


@celery_app.task
def test_background_task(message: str) -> dict:
    print(f"=========================================")
    print(f"Celery воркер успешно принял сообщение: {message}")
    print(f"=========================================")
    return {"status": "success", "msg": message}