from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    path('ws/test/', consumers.TestConsumer.as_asgi()),
    path("ws/random/", consumers.RandomConsumer.as_asgi()),
    re_path(r'ws/prices/$', consumers.PriceConsumer.as_asgi()),
]