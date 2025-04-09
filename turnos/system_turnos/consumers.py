# system_turnos/consumers.py
from channels.db import database_sync_to_async
from .models import Turnos  # Asegúrate de importar tu modelo

class TurnosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("turnos_global", self.channel_name)
        await self.accept()
        print("✅ Conexión WebSocket establecida")  # Debug

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("turnos_global", self.channel_name)

    async def send_turno_update(self, event):
        turnos_data = await self.get_turnos_data()  # Obtiene datos actualizados
        await self.send(text_data=json.dumps({
            "type": "turno_update",
            "data": turnos_data
        }))

    @database_sync_to_async
    def get_turnos_data(self):
        return list(Turnos.objects.values('id', 'numerodeticker', 'estado'))  # Ajusta campos