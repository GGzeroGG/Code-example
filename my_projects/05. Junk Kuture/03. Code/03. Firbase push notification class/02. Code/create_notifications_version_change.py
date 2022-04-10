from apps.main.choices import NotificationType
from apps.main.firebase_notification import FirebaseNotification
from apps.main.models.notification import Notification
from apps.main.templates import NOTIFICATION
from apps.users.choices import UserType
from apps.users.models import User
from apps.users.utils import get_user_avatar_small_or_none

from config.celery import app as celery_app  # noqa


@celery_app.task
def create_notifications_version_change():
    users_ids = User.objects.all().values_list('id', flat=True)
    notification_type = NotificationType.APP_UPDATE.value
    title = NOTIFICATION[notification_type]['title']
    body = NOTIFICATION[notification_type]['body']
    user_admin = User.objects.filter(type=UserType.ADMIN.value).first()
    meta = {
        'avatar_small': get_user_avatar_small_or_none(user=user_admin),
    }
    Notification.objects.bulk_create(
        [
            Notification(
                user_id=user_id,
                title=title,
                body=body,
                meta=meta,
                read=False,
                type=NotificationType.APP_UPDATE.value,
            ) for user_id in users_ids
        ],
        batch_size=500,
    )

    FirebaseNotification().users_send_multicast(
        title=title, body=body, data=meta, user_ids=users_ids,
    )
