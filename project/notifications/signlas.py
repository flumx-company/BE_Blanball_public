from django.db.models.signals import (
    post_save,
    pre_delete,
)
from django.dispatch import receiver
from notifications.constant.notification_types import (
    NOTIFICATION_DELETE_NOTIFICATION_TYPE,
    NOTIFICATION_READ_NOTIFICATION_TYPE,
)
from notifications.models import Notification
from notifications.tasks import send


@receiver(pre_delete, sender=Notification)
def send_update_message_after_delete_notification(
    sender: Notification, instance: Notification, **kwargs
) -> None:
    send(
        user=instance.user,
        data={
            "type": "kafka.message",
            "message": {
                "message_type": NOTIFICATION_DELETE_NOTIFICATION_TYPE,
                "notification": {
                    "id": instance.id,
                },
            },
        },
    )


@receiver(post_save, sender=Notification)
def send_update_message_after_read_notification(
    sender: Notification, instance: Notification, **kwargs
) -> None:
    if instance.type == instance.Type.READ:
        send(
            user=instance.user,
            data={
                "type": "kafka.message",
                "message": {
                    "message_type": NOTIFICATION_READ_NOTIFICATION_TYPE,
                    "notification": {
                        "id": instance.id,
                        "type": instance.type,
                    },
                },
            },
        )
