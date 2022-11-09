from collections import OrderedDict
from datetime import datetime

from django.utils import timezone
from events.constant.response_error import (
    BAD_EVENT_TIME_CREATE_ERROR,
    NO_PRICE_DESK_ERROR,
)
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
)


class EventDateTimeValidator:
    def __call__(self, attrs: OrderedDict) -> OrderedDict:
        date_and_time: datetime = attrs.get("date_and_time")
        price: int = attrs.get("price")
        price_desc: str = attrs.get("price_description")
        if date_and_time - timezone.now() + timezone.timedelta(
            hours=1
        ) < timezone.timedelta(hours=1):
            raise ValidationError(BAD_EVENT_TIME_CREATE_ERROR, HTTP_400_BAD_REQUEST)
        if price and price > 0 and price_desc == None:
            raise ValidationError(NO_PRICE_DESK_ERROR, HTTP_400_BAD_REQUEST)
        if not price and price_desc:
            raise ValidationError(NO_PRICE_DESK_ERROR, HTTP_400_BAD_REQUEST)
        return attrs
