from datetime import datetime
from typing import Any, final

from authentication.models import User
from django.db import models
from django.db.models.query import QuerySet


class Notification(models.Model):
    class Type(models.TextChoices):
        """gender choices"""

        UNREAD: str = "Unread"
        READ: str = "Read"

    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
    type: str = models.CharField(choices=Type.choices, max_length=6, default="Unread")
    time_created: datetime = models.DateTimeField(auto_now_add=True)
    message_type: str = models.CharField(max_length=100)
    data: dict[str, Any] = models.JSONField()

    @final
    def __repr__(self) -> str:
        return "<Notification %s>" % self.id

    @final
    @staticmethod
    def get_all() -> QuerySet["Notification"]:
        return Notification.objects.select_related("user").order_by("-id")

    @final
    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        db_table: str = "notification"
        verbose_name: str = "notification"
        verbose_name_plural: str = "notifications"
