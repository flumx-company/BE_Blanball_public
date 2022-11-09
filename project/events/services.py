import json
import re
from collections import OrderedDict
from datetime import datetime
from typing import (
    Any,
    Callable,
    Generator,
    Optional,
    TypeVar,
    Union,
)

import pandas
from authentication.models import User
from config.exceptions import _404
from django.db import transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone
from events.constant.notification_types import (
    NEW_USER_ON_THE_EVENT_NOTIFICATION_TYPE,
    RESPONSE_TO_THE_INVITE_TO_EVENT_NOTIFICATION_TYPE,
    RESPONSE_TO_THE_REQUEST_FOR_PARTICIPATION_NOTIFICATION_TYPE,
    USER_REMOVE_FROM_EVENT_NOTIFICATION_TYPE,
)
from events.constant.response_error import (
    ALREADY_IN_EVENT_LIKE_SPECTATOR_ERROR,
    ALREADY_IN_EVENT_MEMBERS_LIST_ERROR,
    ALREADY_SENT_REQUEST_TO_PARTICIPATE_ERROR,
    EVENT_AUTHOR_CAN_NOT_JOIN_ERROR,
    EVENT_NOT_FOUND_ERROR,
    GET_PLANNED_EVENTS_ERROR,
)
from events.models import (
    Event,
    InviteToEvent,
    RequestToParticipation,
)
from notifications.tasks import send_to_user
from rest_framework.exceptions import (
    PermissionDenied,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)

bulk = TypeVar(Optional[Generator[list[dict[str, int]], None, None]])


def bulk_delete_events(
    *, data: dict[str, Any], queryset: QuerySet[Event], user: User
) -> bulk:
    for event_id in data:
        try:
            event: Event = queryset.get(id=event_id)
            if event.author == user:
                event.delete()
                yield {"success": event_id}
        except Event.DoesNotExist:
            pass


def bulk_accept_or_decline_invites_to_events(
    *, data: dict[str, Union[list[int], bool]], request_user: User
) -> bulk:
    for invite_id in data["ids"]:
        try:
            invite: InviteToEvent = InviteToEvent.objects.get(id=invite_id)
            if (
                invite.recipient.id == request_user.id
                and invite.status == invite.Status.WAITING
            ):
                if invite.event.current_users.count() < invite.event.amount_members:
                    if data["type"] == True:
                        invite.status = invite.Status.ACCEPTED
                        invite.recipient.current_rooms.add(invite.event)
                    else:
                        invite.status = invite.Status.DECLINED

                    invite.save()
                    send_to_user(
                        user=invite.sender,
                        message_type=RESPONSE_TO_THE_INVITE_TO_EVENT_NOTIFICATION_TYPE,
                        data={
                            "recipient": {
                                "id": invite.sender.id,
                                "name": invite.sender.profile.name,
                                "last_name": invite.sender.profile.last_name,
                            },
                            "event": {
                                "id": invite.event.id,
                                "name": invite.event.name,
                            },
                            "invite": {
                                "id": invite.id,
                                "response": data["type"],
                            },
                            "sender": {
                                "id": invite.recipient.id,
                                "name": invite.recipient.profile.name,
                                "last_name": invite.recipient.profile.last_name,
                            },
                        },
                    )
                    yield {"success": invite_id}

        except InviteToEvent.DoesNotExist:
            pass


def bulk_accpet_or_decline_requests_to_participation(
    *, data: dict[str, Union[list[int], bool]], request_user: User
) -> bulk:
    for request_id in data["ids"]:
        try:
            request_to_p: RequestToParticipation = RequestToParticipation.objects.get(
                id=request_id
            )
            if (
                request_to_p.recipient.id == request_user.id
                and request_to_p.status == request_to_p.Status.WAITING
            ):
                if data["type"] == True:
                    if (
                        request_to_p.event.current_users.count()
                        < request_to_p.event.amount_members
                    ):
                        request_to_p.status = request_to_p.Status.ACCEPTED
                        request_to_p.sender.current_rooms.add(request_to_p.event)
                else:
                    request_to_p.status = request_to_p.Status.DECLINED
                request_to_p.save()
                send_to_user(
                    user=request_to_p.sender,
                    message_type=RESPONSE_TO_THE_REQUEST_FOR_PARTICIPATION_NOTIFICATION_TYPE,
                    data={
                        "recipient": {
                            "id": request_to_p.sender.id,
                            "name": request_to_p.sender.profile.name,
                            "last_name": request_to_p.sender.profile.last_name,
                        },
                        "event": {
                            "id": request_to_p.event.id,
                            "name": request_to_p.event.name,
                        },
                        "request": {
                            "id": request_to_p.id,
                            "response": data["type"],
                        },
                        "sender": {
                            "id": request_to_p.recipient.id,
                            "name": request_to_p.recipient.profile.name,
                            "last_name": request_to_p.recipient.profile.last_name,
                        },
                    },
                )
                yield {"success": request_id}

        except RequestToParticipation.DoesNotExist:
            pass


def event_create(
    *, data: Union[dict[str, Any], OrderedDict[str, Any]], request_user: User
) -> dict[str, Any]:
    data = dict(data)
    users: list[int] = data["current_users"]
    data.pop("current_users")
    try:
        contact_number: str = data["contact_number"]
    except KeyError:
        contact_number: str = str(User.objects.get(id=request_user.id).phone)
    data["contact_number"] = contact_number
    data["date_and_time"] = (
        pandas.to_datetime(data["date_and_time"].isoformat())
        .round("1min")
        .to_pydatetime()
    )
    with transaction.atomic():
        event: Event = Event.objects.create(**data, author=request_user)
        for user in users:
            InviteToEvent.objects.send_invite(
                request_user=request_user, invite_user=user, event=event
            )
        return data


def send_notification_to_subscribe_event_user(
    *,
    event: Event,
    message_type: str,
    start_time: datetime = None,
    time_to_start: int = None,
) -> None:
    for user in list(event.current_users.all()) + list(event.current_fans.all()):
        send_to_user(
            user=user,
            message_type=message_type,
            data={
                "recipient": {
                    "id": user.id,
                    "name": user.profile.name,
                    "last_name": user.profile.last_name,
                },
                "event": {
                    "id": event.id,
                    "start_time": start_time,
                    "time_to_start": time_to_start,
                },
            },
        )


def validate_user_before_join_to_event(*, user: User, event: Event) -> None:
    if user.current_rooms.filter(id=event.id).exists():
        raise ValidationError(ALREADY_IN_EVENT_MEMBERS_LIST_ERROR, HTTP_400_BAD_REQUEST)
    if user.current_views_rooms.filter(id=event.id).exists():
        raise ValidationError(
            ALREADY_IN_EVENT_LIKE_SPECTATOR_ERROR, HTTP_400_BAD_REQUEST
        )
    if event.author.id == user.id:
        raise ValidationError(EVENT_AUTHOR_CAN_NOT_JOIN_ERROR, HTTP_400_BAD_REQUEST)
    if user in event.black_list.all():
        raise PermissionDenied()
    if RequestToParticipation.objects.filter(
        sender=user, event=event.id, recipient=event.author
    ):
        raise ValidationError(
            ALREADY_SENT_REQUEST_TO_PARTICIPATE_ERROR, HTTP_400_BAD_REQUEST
        )


def send_notification_to_event_author(*, event: Event, request_user: User) -> None:
    send_to_user(
        user=User.objects.get(id=event.author.id),
        message_type=NEW_USER_ON_THE_EVENT_NOTIFICATION_TYPE,
        data={
            "recipient": {
                "id": event.author.id,
                "name": event.author.profile.name,
                "last_name": event.author.profile.last_name,
            },
            "event": {
                "id": event.id,
                "name": event.name,
            },
            "sender": {
                "id": request_user.id,
                "name": request_user.profile.name,
                "last_name": request_user.profile.last_name,
            },
        },
    )


def validate_get_user_planned_events(*, pk: int, request_user: User) -> None:
    user: User = User.objects.get(id=pk)
    if (
        user.configuration["show_my_planned_events"] == False
        and request_user.id != user.id
    ):
        raise ValidationError(GET_PLANNED_EVENTS_ERROR, HTTP_400_BAD_REQUEST)


def filter_event_by_user_planned_events_time(
    *, pk: int, queryset: QuerySet[Event]
) -> QuerySet[Event]:
    user: User = User.objects.get(id=pk)
    num: str = re.findall(r"\d{1,10}", user.get_planned_events)[0]
    string: str = re.findall(r"\D", user.get_planned_events)[0]
    if string == "d":
        num: int = int(num[0])
    elif string == "m":
        num: int = int(num[0]) * 30 + int(num[0]) // 2
    elif string == "y":
        num: int = int(num[0]) * 365
    finish_date: datetime = timezone.now() + timezone.timedelta(days=int(num))
    return queryset.filter(
        author_id=user.id, date_and_time__range=[timezone.now(), finish_date]
    )


def only_author(Object):
    def wrap(
        func: Callable[[Request, int, ...], Response]
    ) -> Callable[[Request, int, ...], Response]:
        def called(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Any:
            try:
                if self.request.user.id == Object.objects.get(id=pk).author.id:
                    return func(self, request, pk, *args, **kwargs)
                raise PermissionDenied()
            except Object.DoesNotExist:
                raise _404(object=Object)

        return called

    return wrap


def not_in_black_list(
    func: Callable[[Request, int, ...], Response]
) -> Callable[[Request, int, ...], Response]:
    def wrap(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Any:
        try:
            if request.user in Event.objects.get(id=pk).black_list.all():
                raise PermissionDenied()
            return func(self, request, pk, *args, **kwargs)
        except Event.DoesNotExist:
            raise _404(object=Event)

    return wrap


def remove_user_from_event(*, user: User, event: Event, reason: str) -> None:
    user.current_rooms.remove(event)
    event.black_list.add(user)
    send_to_user(
        user=user,
        message_type=USER_REMOVE_FROM_EVENT_NOTIFICATION_TYPE,
        data={
            "recipient": {
                "id": user.id,
                "name": user.profile.name,
                "last_name": user.profile.last_name,
            },
            "reason": {"text": reason},
            "event": {
                "id": event.id,
                "name": event.name,
            },
        },
    )


def skip_objects_from_response_by_id(
    func: Callable[[..., ...], QuerySet[Any]]
) -> Callable[[..., ...], QuerySet[Any]]:
    def wrap(self, *args: Any, **kwargs: Any) -> Any:
        try:
            self.queryset = self.queryset.filter(
                ~Q(id__in=list(self.request.query_params["skipids"].split(",")))
            )
            return func(self, *args, **kwargs)
        except KeyError:
            pass
        except ValueError:
            pass
        finally:
            return func(self, *args, **kwargs)

    return wrap
