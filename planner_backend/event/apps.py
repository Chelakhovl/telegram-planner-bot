from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event"

    def ready(self):
        from .scheduler import create_periodic_task

        create_periodic_task()
