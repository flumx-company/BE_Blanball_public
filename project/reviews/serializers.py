from collections import OrderedDict
from typing import Any, Union

from authentication.models import User
from notifications.tasks import send_to_user
from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
)
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)
from reviews.constant.errors import (
    REVIEW_CREATE_ERROR,
)
from reviews.constant.notification_types import (
    REVIEW_CREATE_NOTIFICATION_TYPE,
)
from reviews.models import Review


class CreateReviewSerializer(ModelSerializer):
    class Meta:
        model: Review = Review
        exclude: Union[str, list[str]] = [
            "email",
        ]

    def validate(self, attrs) -> OrderedDict:
        user: User = attrs.get("user")

        if self.context["request"].user.email == user.email:
            raise ValidationError(REVIEW_CREATE_ERROR, HTTP_400_BAD_REQUEST)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Review:
        user: User = User.objects.get(email=validated_data["user"])
        review: Review = Review.objects.create(
            email=self.context["request"].user.email, **validated_data
        )
        send_to_user(
            user=user,
            message_type=REVIEW_CREATE_NOTIFICATION_TYPE,
            data={
                "recipient": {
                    "id": user.id,
                    "name": user.profile.name,
                    "last_name": user.profile.last_name,
                },
                "review": {
                    "id": review.id,
                },
                "sender": {
                    "id": self.context["request"].user.id,
                    "name": self.context["request"].user.profile.name,
                    "last_name": self.context["request"].user.profile.last_name,
                },
            },
        )
        user: User = User.objects.get(email=validated_data["user"])
        for item in user.reviews.all():
            stars = item.stars
        user.raiting = stars / user.reviews.count()
        user.save()
        return review


class ReviewListSerializer(ModelSerializer):
    class Meta:
        model: Review = Review
        fields: Union[str, list[str]] = "__all__"


class ReviewUpdateSerializer(ModelSerializer):
    class Meta:
        model: Review = Review
        fields: Union[str, list[str]] = [
            "text",
            "stars",
        ]
