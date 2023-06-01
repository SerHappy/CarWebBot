from celery import Celery
from celery.schedules import crontab

import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "publish_every_minute": {
        "task": "apps.bot.tasks.publish_announcements",
        "schedule": crontab(),
    },
}
