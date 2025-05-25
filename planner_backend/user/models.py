from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, telegram_id, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError("Telegram ID is required")
        user = self.model(telegram_id=telegram_id, **extra_fields)
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, telegram_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.model(telegram_id=telegram_id, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50, blank=True)
    language = models.CharField(
        max_length=5, choices=[("ua", "Ukrainian"), ("en", "English")], default="ua"
    )
    timezone = models.CharField(max_length=50, default="UTC")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.telegram_id)
