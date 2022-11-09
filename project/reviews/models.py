from datetime import datetime
from typing import final

from authentication.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models.query import QuerySet


class Review(models.Model):
    email: str = models.EmailField(max_length=255, db_index=True)
    text: str = models.CharField(max_length=200)
    time_created: datetime = models.DateTimeField(auto_now_add=True)
    stars: int = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    user: User = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="reviews"
    )

    @final
    def __repr__(self) -> str:
        return "<Review %s>" % self.id

    @final
    @staticmethod
    def get_all() -> QuerySet["Review"]:
        return Review.objects.select_related("user").order_by("-id")

    @final
    def __str__(self) -> str:
        return self.email

    class Meta:
        db_table: str = "review"
        verbose_name: str = "review"
        verbose_name_plural: str = "reviews"
