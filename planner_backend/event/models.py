from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from user.models import User


class PeriodicityChoices(models.TextChoices):
    ONCE = "once", "Одноразова"
    DAILY = "daily", "Щоденна"
    WEEKLY = "weekly", "Щотижнева"
    MONTHLY = "monthly", "Щомісячна"
    YEARLY = "yearly", "Щорічна"


CATEGORY_CHOICES = [
    ("work", "Work"),
    ("study", "Study"),
    ("personal", "Personal"),
    ("health", "Health"),
    ("other", "Other"),
]


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    periodicity = models.CharField(
        max_length=20,
        choices=PeriodicityChoices.choices,
        default=PeriodicityChoices.ONCE,
    )
    reminder_minutes = models.IntegerField(
        default=10, validators=[MinValueValidator(0), MaxValueValidator(1440)]
    )
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    tags = models.TextField(blank=True)
    notified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "date_time"]),
            models.Index(fields=["notified"]),
        ]
        unique_together = ("user", "name", "date_time")

    def __str__(self):
        return f"{self.name} ({self.date_time.strftime('%Y-%m-%d %H:%M')})"

    def get_reminder_time(self):
        return self.date_time - timedelta(minutes=self.reminder_minutes)
