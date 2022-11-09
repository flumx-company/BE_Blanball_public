from datetime import datetime
from typing import Any, Union

from asgiref.sync import async_to_sync
from authentication.models import User
from channels.layers import get_channel_layer
from config.celery import app
from django.db.models import QuerySet
from notifications.constant.notification_types import (
    CHANGE_MAINTENANCE_NOTIFICATION_TYPE,
)
from notifications.models import Notification


@app.task(
    ignore_result=True,
    time_limit=5,
    soft_time_limit=3,
    default_retry_delay=5,
)
def send(user: User, data: dict[str, Any]) -> None:
    async_to_sync(get_channel_layer().group_send)(user.group_name, data)


def send_to_user(
    user: User,
    message_type: str,
    data: dict[str, Union[str, int, datetime, bool]] = None,
) -> None:
    if message_type != CHANGE_MAINTENANCE_NOTIFICATION_TYPE:
        notification = Notification.objects.create(
            user=user, message_type=message_type, data=data
        )
    send(
        user=user,
        data={
            "type": "kafka.message",
            "message": {
                "message_type": message_type,
                "notification_id": notification.id,
                "data": data,
            },
        },
    )


@app.task(
    ignore_result=True,
    time_limit=5,
    soft_time_limit=3,
    default_retry_delay=5,
)
def read_all_user_notifications(*, request_user_id: int) -> None:
    for notification in Notification.get_all().filter(
        user_id=request_user_id, type=Notification.Type.UNREAD
    ):
        notification.type = notification.Type.READ
        notification.save()


@app.task(
    ignore_result=True,
    time_limit=5,
    soft_time_limit=3,
    default_retry_delay=5,
)
def delete_all_user_notifications(*, request_user_id: int) -> None:
    Notification.get_all().filter(user_id=request_user_id).delete()
