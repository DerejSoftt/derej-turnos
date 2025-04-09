# system_turnos/routing.py
from django.urls import path
from . import consumers

# system_turnos/routing.py
websocket_urlpatterns = [
    path('ws/turnos/', consumers.TurnosConsumer.as_asgi()),  # ¡Agrega la barra final!
]