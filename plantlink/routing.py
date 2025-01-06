from django.urls import path
from .consumer import SensorDataConsumer

websocket_urlpatterns = [
    path('ws/sensor_data/', SensorDataConsumer.as_asgi()),
]