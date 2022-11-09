import os

from channels.routing import (
    ProtocolTypeRouter,
    URLRouter,
)
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")


django_asgi_app = get_asgi_application()
import notifications.routing
from authentication.middlewares import (
    JwtAuthMiddlewareStack,
)

application = ProtocolTypeRouter(
    {
        "websocket": JwtAuthMiddlewareStack(
            URLRouter(notifications.routing.websocket_urlpatterns)
        ),
        "http": django_asgi_app,
    }
)
