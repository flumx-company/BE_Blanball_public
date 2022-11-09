from collections import OrderedDict
from typing import Any, Union

from authentication.models import User
from authentication.serializers import (
    EventUsersSerializer,
)
from config.exceptions import _404
from events.constant.response_error import (
    ALREADY_IN_EVENT_FANS_LIST_ERROR,
    ALREADY_IN_EVENT_MEMBERS_LIST_ERROR,
    EVENT_NOT_FOUND_ERROR,
    EVENT_TIME_EXPIRED_ERROR,
    NO_EVENT_PLACE_ERROR,
    NO_IN_EVENT_MEMBERS_LIST_ERROR,
)
from events.models import (
    Event,
    InviteToEvent,
    RequestToParticipation,
)
from events.validators import (
    EventDateTimeValidator,
)
from rest_framework import serializers
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model: Event = Event
        validators = [EventDateTimeValidator()]
        exclude: Union[str, list[str]] = [
            "author",
            "status",
            "current_fans",
            "black_list",
        ]


class UpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model: Event = Event
        validators = [EventDateTimeValidator()]
        exclude: Union[str, list[str]] = [
            "author",
            "status",
            "current_fans",
            "current_users",
            "black_list",
        ]

    def update(self, instance, validated_data: dict) -> OrderedDict:
        return super().update(instance, validated_data)


class EventSerializer(serializers.ModelSerializer):
    author = EventUsersSerializer()
    current_users = EventUsersSerializer(many=True)

    class Meta:
        model: Event = Event
        fields: Union[str, list[str]] = "__all__"


class PopularIventsListSerializer(serializers.ModelSerializer):
    class Meta:
        model: Event = Event
        fields: Union[str, list[str]] = [
            "author",
            "id",
            "name",
            "place",
            "gender",
            "date_and_time",
            "type",
        ]


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model: Event = Event
        fields: Union[str, list[str]] = [
            "author",
            "id",
            "name",
            "place",
            "amount_members",
            "status",
            "gender",
            "price",
            "type",
            "need_ball",
            "duration",
            "need_form",
            "privacy",
            "date_and_time",
            "count_current_users",
            "count_current_fans",
        ]


class InInvitesEventSerializer(serializers.ModelSerializer):
    class Meta:
        model: Event = Event
        fields: Union[str, list[str]] = [
            "id",
            "name",
            "date_and_time",
        ]


class InvitesToEventListSerializer(serializers.ModelSerializer):
    event = InInvitesEventSerializer()
    sender = EventUsersSerializer()

    class Meta:
        model: InviteToEvent = InviteToEvent
        fields: Union[str, list[str]] = ["id", "time_created", "event", "sender"]


class DeleteIventsSerializer(serializers.Serializer):
    ids: list[int] = serializers.ListField(child=serializers.IntegerField(min_value=0))

    class Meta:
        fieds: Union[str, list[str]] = [
            "ids",
        ]


class JoinOrRemoveRoomSerializer(serializers.Serializer):
    event_id: int = serializers.IntegerField(min_value=0)

    class Meta:
        fields: Union[str, list[str]] = [
            "event_id",
        ]

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        event_id: int = attrs.get("event_id")
        try:
            event: Event = Event.objects.get(id=event_id)
            if event.status != event.Status.PLANNED:
                raise serializers.ValidationError(
                    EVENT_TIME_EXPIRED_ERROR, HTTP_400_BAD_REQUEST
                )
            if event.amount_members < event.count_current_users + 1:
                raise serializers.ValidationError(
                    NO_EVENT_PLACE_ERROR, HTTP_400_BAD_REQUEST
                )
            return super().validate(attrs)
        except Event.DoesNotExist:
            raise _404(object=Event)


class InviteUserToEventSerializer(serializers.Serializer):
    user_id: int = serializers.IntegerField(min_value=0)
    event_id: int = serializers.IntegerField(min_value=0)

    class Meta:
        fields: Union[str, list[str]] = [
            "event_id",
            "user_id",
        ]

    def validate(self, attrs) -> OrderedDict[str, Any]:
        try:
            invite_user: User = User.objects.get(id=attrs.get("user_id"))
            event: Event = Event.objects.get(id=attrs.get("event_id"))
            if event.status == Event.Status.FINISHED:
                raise serializers.ValidationError(
                    EVENT_TIME_EXPIRED_ERROR, HTTP_400_BAD_REQUEST
                )
            if invite_user.current_rooms.filter(id=event.id).exists():
                raise serializers.ValidationError(
                    ALREADY_IN_EVENT_MEMBERS_LIST_ERROR, HTTP_400_BAD_REQUEST
                )
            if invite_user.current_views_rooms.filter(id=event.id).exists():
                raise serializers.ValidationError(
                    ALREADY_IN_EVENT_FANS_LIST_ERROR, HTTP_400_BAD_REQUEST
                )
            return super().validate(attrs)
        except User.DoesNotExist:
            raise _404(object=User)
        except Event.DoesNotExist:
            raise _404(object=Event)


class RemoveUserFromEventSerializer(serializers.Serializer):
    user_id: int = serializers.IntegerField(min_value=0)
    event_id: int = serializers.IntegerField(min_value=0)
    reason: str = serializers.CharField(max_length=255)

    class Meta:
        fields: Union[str, list[str]] = [
            "event_id",
            "user_id",
            "reason",
        ]

    def validate(self, attrs) -> OrderedDict[str, Any]:
        try:
            removed_user: User = User.objects.get(id=attrs.get("user_id"))
            event: Event = Event.objects.get(id=attrs.get("event_id"))
            if event.status == event.Status.FINISHED:
                raise serializers.ValidationError(
                    EVENT_TIME_EXPIRED_ERROR, HTTP_400_BAD_REQUEST
                )
            if not removed_user.current_rooms.filter(id=event.id).exists():
                raise serializers.ValidationError(
                    NO_IN_EVENT_MEMBERS_LIST_ERROR, HTTP_400_BAD_REQUEST
                )
            return super().validate(attrs)
        except User.DoesNotExist:
            raise _404(object=User)
        except Event.DoesNotExist:
            raise _404(object=Event)


class RequestToParticipationSerializer(serializers.ModelSerializer):
    sender = EventUsersSerializer()
    event = InInvitesEventSerializer()

    class Meta:
        model: RequestToParticipation = RequestToParticipation
        fields: Union[str, list[str]] = "__all__"


class BulkAcceptOrDeclineRequestToParticipationSerializer(serializers.Serializer):
    ids: list[int] = serializers.ListField(child=serializers.IntegerField(min_value=0))
    type: bool = serializers.BooleanField()

    class Meta:
        fields: Union[str, list[str]] = [
            "ids",
            "type",
        ]
