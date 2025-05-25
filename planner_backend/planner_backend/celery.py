import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planner_backend.settings")

app = Celery("planner_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
