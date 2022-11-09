from typing import Type

from config.yasg import skip_param
from django.db.models.query import QuerySet
from django.utils.decorators import (
    method_decorator,
)
from drf_yasg.utils import swagger_auto_schema
from events.services import (
    skip_objects_from_response_by_id,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
)
from rest_framework.serializers import Serializer
from reviews.models import Review
from reviews.serializers import (
    CreateReviewSerializer,
    ReviewListSerializer,
)


class ReviewCreate(CreateAPIView):
    serializer_class: Type[Serializer] = CreateReviewSerializer
    queryset: QuerySet[Review] = Review.get_all()


@method_decorator(swagger_auto_schema(manual_parameters=[skip_param]), name="get")
class UserReviewsList(ListAPIView):
    serializer_class: Type[Serializer] = ReviewListSerializer
    queryset: QuerySet[Review] = Review.get_all()

    @skip_objects_from_response_by_id
    def get_queryset(self) -> QuerySet[Review]:
        return self.queryset.filter(user=self.request.user.id)
