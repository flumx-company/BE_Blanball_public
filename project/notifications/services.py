import json
from typing import (
    Any,
    Generator,
    Optional,
    TypeVar,
)

from asgiref.sync import async_to_sync
from authentication.models import User
from channels.layers import get_channel_layer
from django.db.models.query import QuerySet
from notifications.constant.notification_types import (
    CHANGE_MAINTENANCE_NOTIFICATION_TYPE,
)
from notifications.models import Notification

bulk = TypeVar(Optional[Generator[list[dict[str, int]], None, None]])


def update_maintenance(*, data: dict[str, str]) -> None:

    with open("./config/config.json", "r") as f:
        json_data = json.load(f)
        json_data["isMaintenance"] = data["isMaintenance"]

    with open("./config/config.json", "w") as f:
        f.write(json.dumps(json_data))

        async_to_sync(get_channel_layer().group_send)(
            "general",
            {
                "type": "general.message",
                "message": {
                    "message_type": CHANGE_MAINTENANCE_NOTIFICATION_TYPE,
                    "data": {
                        "maintenance": {
                            "type": data["isMaintenance"],
                        }
                    },
                },
            },
        )


def bulk_delete_notifications(
    *, data: dict[str, Any], queryset: QuerySet[Notification], user: User
) -> bulk:
    for notification in data:
        try:
            notify = queryset.get(id=notification)
            if notify.user == user:
                notify.delete()
                yield {"success": notification}
        except Notification.DoesNotExist:
            pass


def bulk_read_notifications(
    *, data: dict[str, Any], queryset: QuerySet[Notification]
) -> bulk:
    for notification in data:
        try:
            notify = queryset.get(id=notification)
            if notify.type != "Read":
                notify.type = "Read"
                notify.save()
                yield {"success": notification}
        except Notification.DoesNotExist:
            pass
