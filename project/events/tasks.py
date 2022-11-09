from config.celery import app
from django.db.models import Q
from django.utils import timezone
from events.constant.notification_types import (
    EVENT_TIME_NOTIFICATION_TYPE,
)
from events.models import Event
from events.services import (
    send_notification_to_subscribe_event_user,
)


@app.task
def check_event_start_time() -> None:
    for event in Event.get_all().filter(~Q(status=Event.Status.FINISHED)):
        if event.date_and_time - timezone.now() == timezone.timedelta(minutes=1440):
            send_notification_to_subscribe_event_user(
                event=event,
                message_type=EVENT_TIME_NOTIFICATION_TYPE,
                start_time=str(event.date_and_time),
                time_to_start=1440,
            )
        elif event.date_and_time - timezone.now() == timezone.timedelta(minutes=120):
            send_notification_to_subscribe_event_user(
                event=event,
                message_type=EVENT_TIME_NOTIFICATION_TYPE,
                start_time=str(event.date_and_time),
                time_to_start=120,
            )
        elif event.date_and_time - timezone.now() == timezone.timedelta(minutes=10):
            send_notification_to_subscribe_event_user(
                event=event,
                message_type=EVENT_TIME_NOTIFICATION_TYPE,
                start_time=str(event.date_and_time),
                time_to_start=10,
            )
        elif event.date_and_time == timezone.now():
            event.status = event.Status.ACTIVE
            event.save()
        elif (
            (event.date_and_time - timezone.now()) / timezone.timedelta(days=1)
        ) * 1440 + event.duration <= 0:
            event.status = event.Status.FINISHED
            event.save()
