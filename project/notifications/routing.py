from typing import Union

from django.urls import path
from django.urls.resolvers import (
    URLPattern,
    URLResolver,
)
from notifications.consumers import (
    GeneralConsumer,
    UserConsumer,
)

websocket_urlpatterns: list[Union[URLResolver, URLPattern]] = [
    path("ws/notifications/", UserConsumer.as_asgi(), name="user-notifications"),
    path("ws/general/", GeneralConsumer.as_asgi(), name="general"),
]
