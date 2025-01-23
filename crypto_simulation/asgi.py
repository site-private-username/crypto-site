
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Make sure to set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_simulation.settings')
django.setup()

# Import your routing (see next step)
from trading.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})