from typing import Union

from django_filters import (
    rest_framework as filters,
)
from events.models import Event


class EventDateTimeRangeFilter(filters.FilterSet):
    date_and_time = filters.DateFromToRangeFilter()

    class Meta:
        model: Event = Event
        fields: Union[str, list[str]] = [
            "date_and_time",
            "type",
            "need_ball",
            "gender",
            "status",
            "duration",
        ]
