from asgiref.sync import sync_to_async
from user.models import User
import logging

logger = logging.getLogger("user")


@sync_to_async
def get_or_create_user(telegram_id: int) -> User:
    try:
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "language": "ua",
                "timezone": "UTC",
            },
        )
        if created:
            logger.info(f"New user created: {telegram_id}")
        return user
    except Exception as e:
        logger.exception(f"Failed to get or create user {telegram_id}: {e}")
        raise
