from gettext import install
from typing import Any, Union

from authentication.models import User
from django.db.models.signals import (
    m2m_changed,
    post_save,
    pre_delete,
)
from django.dispatch import receiver
from events.constant.notification_types import (
    EVENT_DELETE_NOTIFICATION_TYPE,
    EVENT_HAS_BEEN_ENDEN_NOTIFICATION_TYPE,
    INVITE_USER_TO_EVENT_NOTIFICATION_TYPE,
    LAST_USER_ON_THE_EVENT_NOTIFICATION_TYPE,
    NEW_REQUEST_TO_PARTICIPATION_NOTIFICATION_TYPE,
    UPDATE_MESSAGE_ACCEPT_OR_DECLINE_INVITE_TO_EVENT,
    UPDATE_MESSAGE_ACCEPT_OR_DECLINE_REQUEST_TO_PARTICIPATION,
    YOU_ARE_LAST_USER_ON_THE_EVENT_NOTIFICATION_TYPE,
)
from events.models import (
    Event,
    InviteToEvent,
    RequestToParticipation,
)
from events.services import (
    send_notification_to_subscribe_event_user,
)
from notifications.models import Notification
from notifications.tasks import send, send_to_user


def send_to_all_event_users(
    *, event: Event, message_type: str, data: dict[str, Any]
) -> None:
    for user in list(event.current_users.all()) + [event.author]:
        send_to_user(user, message_type=message_type, data=data)


@receiver(m2m_changed, sender=Event.current_users.through)
def send_message_when_last_user_join_to_event(
    sender: User, instance: User, **kwargs: Any
) -> None:
    action: str = kwargs.pop("action", None)
    if action == "post_add":
        event: Event = instance.current_rooms.through.objects.last().event
        if event.current_users.all().count() + 1 == event.amount_members:
            for user in list(event.current_users.all()) + [event.author]:
                if user == instance:
                    message_type: str = YOU_ARE_LAST_USER_ON_THE_EVENT_NOTIFICATION_TYPE
                else:
                    message_type: str = LAST_USER_ON_THE_EVENT_NOTIFICATION_TYPE
                send_to_user(
                    user,
                    message_type=message_type,
                    data={
                        "event": {
                            "id": event.id,
                            "name": event.name,
                        }
                    },
                )


@receiver(post_save, sender=Event)
def send_message_the_end_of_event(sender: Event, instance: Event, **kwargs) -> None:
    if instance.status == instance.Status.FINISHED:
        send_to_all_event_users(
            event=instance,
            message_type=EVENT_HAS_BEEN_ENDEN_NOTIFICATION_TYPE,
            data={
                "event": {
                    "id": instance.id,
                    "name": instance.name,
                }
            },
        )


@receiver(post_save, sender=Event)
def delete_all_event_relations_after_finished(
    sender: Event, instance: Event, **kwargs
) -> None:
    if instance.status == instance.Status.FINISHED:
        instance.invites.all().delete()
        for notification in Notification.objects.filter(data__event__id=instance.id):
            notification.data["event"].update({"finished": True})
            notification.save()


@receiver(pre_delete, sender=Event)
def delete_event(sender: Event, instance: Event, **kwargs) -> None:
    send_notification_to_subscribe_event_user(
        event=instance, message_type=EVENT_DELETE_NOTIFICATION_TYPE
    )


def send_update_message_after_response(
    *, instance: Union[InviteToEvent, RequestToParticipation], message_type: str
) -> None:
    if instance.status != instance.Status.WAITING:
        try:
            status: dict[str, bool] = {
                instance.Status.ACCEPTED: True,
                instance.Status.DECLINED: False,
            }
            notification = Notification.objects.get(
                message_type=INVITE_USER_TO_EVENT_NOTIFICATION_TYPE,
                data__invite__id=instance.id,
            )
            send(
                user=instance.recipient,
                data={
                    "type": "kafka.message",
                    "message": {
                        "message_type": message_type,
                        "notification": {
                            "id": notification.id,
                            "message_type": notification.message_type,
                            "response": status[instance.status],
                        },
                    },
                },
            )
            notification.data.update({"response": status[instance.status]})
            notification.save()

        except Notification.DoesNotExist:
            pass


@receiver(post_save, sender=InviteToEvent)
def send_message_after_response_to_invite_to_event(
    sender: InviteToEvent, instance: InviteToEvent, **kwargs: Any
) -> None:
    send_update_message_after_response(
        instance=instance, message_type=UPDATE_MESSAGE_ACCEPT_OR_DECLINE_INVITE_TO_EVENT
    )


@receiver(post_save, sender=RequestToParticipation)
def send_message_after_response_to_request_to_participation(
    sender: RequestToParticipation, instance: RequestToParticipation, **kwargs: Any
) -> None:
    send_update_message_after_response(
        instance=instance,
        message_type=UPDATE_MESSAGE_ACCEPT_OR_DECLINE_REQUEST_TO_PARTICIPATION,
    )


@receiver(post_save, sender=RequestToParticipation)
def after_send_request_to_PARTICIPATION(
    sender: RequestToParticipation, instance: RequestToParticipation, **kwargs: Any
) -> None:
    if instance.status == instance.Status.WAITING:
        send_to_user(
            user=instance.recipient,
            message_type=NEW_REQUEST_TO_PARTICIPATION_NOTIFICATION_TYPE,
            data={
                "recipient": {
                    "id": instance.recipient.id,
                    "name": instance.recipient.profile.name,
                    "last_name": instance.recipient.profile.last_name,
                },
                "request": {"id": instance.id},
                "sender": {
                    "id": instance.sender.id,
                    "name": instance.sender.profile.name,
                    "last_name": instance.sender.profile.last_name,
                },
                "event": {
                    "id": instance.event.id,
                    "name": instance.event.name,
                },
            },
        )
