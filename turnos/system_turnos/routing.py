from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/turnos/', consumers.TurnosConsumer.as_asgi()),
]