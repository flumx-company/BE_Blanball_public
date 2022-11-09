import profile
from datetime import date, datetime
from email.policy import default
from typing import Any, Optional, final

from authentication.models import Gender, User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models.query import QuerySet
from events.constant.notification_types import (
    INVITE_USER_TO_EVENT_NOTIFICATION_TYPE,
)
from events.constant.response_error import (
    AUTHOR_CAN_NOT_INVITE_ERROR,
    SENT_INVATION_ERROR,
    THIS_USER_CAN_NOT_BE_INVITED,
    USER_CAN_NOT_INVITE_TO_THIS_EVENT_ERROR,
)
from notifications.tasks import send_to_user
from phonenumber_field.modelfields import (
    PhoneNumberField,
)
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.status import (
    HTTP_403_FORBIDDEN,
)


class Event(models.Model):
    """footbal ivent model"""

    class Type(models.TextChoices):
        """ivent  type choices"""

        FOOTBALL: str = "Football"
        FUTSAL: str = "Futsal"

    class CloseType(models.TextChoices):
        SHIRT_FRONT: str = "Shirt-Front"
        T_SHIRT: str = "T-Shirt"
        ANY: str = "Any"

    class Status(models.TextChoices):
        PLANNED: str = "Planned"
        ACTIVE: str = "Active"
        FINISHED: str = "Finished"

    class Duration(models.IntegerChoices):
        MINUTES_10: int = 10
        MINUTES_20: int = 20
        MINUTES_30: int = 30
        MINUTES_40: int = 40
        MINUTES_50: int = 50
        MINUTES_60: int = 60
        MINUTES_70: int = 70
        MINUTES_80: int = 80
        MINUTES_90: int = 90
        MINUTES_100: int = 100
        MINUTES_110: int = 110
        MINUTES_120: int = 120
        MINUTES_130: int = 130
        MINUTES_140: int = 140
        MINUTES_150: int = 150
        MINUTES_160: int = 160
        MINUTES_170: int = 170
        MINUTES_180: int = 180

    author: User = models.ForeignKey(User, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=255)
    description: str = models.TextField()
    place: str = models.CharField(max_length=255)
    gender: str = models.CharField(choices=Gender.choices, max_length=10)
    date_and_time: datetime = models.DateTimeField()
    contact_number: str = PhoneNumberField(null=True)
    need_ball: bool = models.BooleanField()
    amount_members: int = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(50)], default=6
    )
    type: str = models.CharField(choices=Type.choices, max_length=15)
    price: int = models.PositiveSmallIntegerField(
        null=True, validators=[MinValueValidator(1)]
    )
    price_description: str = models.CharField(max_length=500, null=True)
    need_form: bool = models.BooleanField()
    privacy: bool = models.BooleanField()
    duration: int = models.PositiveSmallIntegerField(choices=Duration.choices)
    forms: str = models.CharField(choices=CloseType.choices, max_length=15)
    status: str = models.CharField(
        choices=Status.choices, max_length=10, default="Planned"
    )
    current_users: list[User] = models.ManyToManyField(
        User, related_name="current_rooms", blank=True
    )
    current_fans: list[User] = models.ManyToManyField(
        User, related_name="current_views_rooms", blank=True
    )
    black_list: list[User] = models.ManyToManyField(
        User, related_name="black_list", blank=True
    )

    @property
    def count_current_users(self) -> int:
        return self.current_users.count()

    @property
    def count_current_fans(self) -> int:
        return self.current_fans.count()

    @final
    def __repr__(self) -> str:
        return "<Event %s>" % self.id

    @final
    def __str__(self) -> str:
        return self.name

    @final
    @staticmethod
    def get_all() -> QuerySet["Event"]:
        return (
            Event.objects.select_related("author")
            .prefetch_related("current_users", "current_fans")
            .order_by("-id")
        )

    class Meta:
        db_table: str = "event"
        verbose_name: str = "event"
        verbose_name_plural: str = "events"


class RequestToParticipation(models.Model):
    class Status(models.TextChoices):
        WAITING: str = "Waiting"
        ACCEPTED: str = "Accepted"
        DECLINED: str = "Declined"

    recipient: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient"
    )
    time_created: datetime = models.DateTimeField(auto_now_add=True)
    event: Event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="invites"
    )
    sender: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    status: str = models.CharField(
        choices=Status.choices, max_length=10, default=Status.WAITING
    )

    # def _type(self):
    #     return self.__class__.__name__

    def __repr__(self) -> str:
        return "<RequestToParticipation %s>" % self.id

    def __str__(self) -> str:
        return self.recipient.email

    @staticmethod
    def get_all() -> QuerySet["RequestToParticipation"]:
        return RequestToParticipation.objects.select_related(
            "recipient", "event", "sender"
        ).order_by("-id")

    class Meta:
        db_table: str = "request_to_participation"
        verbose_name: str = "request to participation"
        verbose_name_plural: str = "requests to participation"


class InviteToEventManager(models.Manager):
    def send_invite(
        self, request_user: User, invite_user: User, event: Event
    ) -> "InviteToEvent":

        if invite_user.id == request_user.id:
            raise ValidationError(SENT_INVATION_ERROR, HTTP_403_FORBIDDEN)
        if invite_user.id == event.author.id:
            raise ValidationError(AUTHOR_CAN_NOT_INVITE_ERROR, HTTP_403_FORBIDDEN)
        if invite_user in event.black_list.all():
            raise ValidationError(THIS_USER_CAN_NOT_BE_INVITED, HTTP_403_FORBIDDEN)
        if InviteToEvent.objects.filter(
            recipient=invite_user, event=event, status=InviteToEvent.Status.DECLINED
        ).exists():
            raise ValidationError(THIS_USER_CAN_NOT_BE_INVITED, HTTP_403_FORBIDDEN)

        if (
            request_user.id == event.author.id
            or request_user in event.current_users.all()
        ):
            invite = self.model(recipient=invite_user, event=event, sender=request_user)
            invite.save()
            send_to_user(
                user=invite_user,
                message_type=INVITE_USER_TO_EVENT_NOTIFICATION_TYPE,
                data={
                    "recipient": {
                        "id": invite_user.id,
                        "name": invite_user.profile.name,
                        "last_name": invite_user.profile.last_name,
                    },
                    "event": {"id": event.id, "name": event.name},
                    "invite": {
                        "id": invite.id,
                    },
                    "sender": {
                        "id": request_user.id,
                        "name": request_user.profile.name,
                        "last_name": request_user.profile.last_name,
                    },
                },
            )
            return invite
        else:
            raise ValidationError(
                USER_CAN_NOT_INVITE_TO_THIS_EVENT_ERROR, HTTP_403_FORBIDDEN
            )


class InviteToEvent(RequestToParticipation):

    objects = InviteToEventManager()

    @final
    def __repr__(self) -> str:
        return "<InviteToEvent %s>" % self.id

    @final
    def __str__(self) -> str:
        return self.recipient.profile.name

    @final
    @staticmethod
    def get_all() -> QuerySet["InviteToEvent"]:
        return InviteToEvent.objects.select_related(
            "recipient", "event", "sender"
        ).order_by("-id")

    class Meta:
        db_table: str = "invite_to_event"
        verbose_name: str = "invite to event"
        verbose_name_plural: str = "invites to event"
