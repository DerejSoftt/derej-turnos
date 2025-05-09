import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Turnos

class TurnosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Unirse al grupo 'turnos'
        await self.channel_layer.group_add(
            "turnos",
            self.channel_name
        )
        await self.accept()
        print("Cliente WebSocket conectado")

    async def disconnect(self, close_code):
        # Abandonar el grupo al desconectar
        await self.channel_layer.group_discard(
            "turnos",
            self.channel_name
        )
        print(f"Cliente WebSocket desconectado, código: {close_code}")

    # Recibir mensaje desde WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            print(f"Mensaje recibido: {message}")
            
            # Puedes implementar más lógica aquí si necesitas procesar mensajes
            # del cliente
            
        except json.JSONDecodeError:
            print("Error: Datos recibidos no son JSON válido")
        except Exception as e:
            print(f"Error al procesar mensaje: {str(e)}")

    # Método llamado desde el channel_layer
    async def recibir_llamado(self, event):
        try:
            turno_id = event["turno_id"]
            turno = await self.get_turno_info(turno_id)
            
            if turno:
                # Enviar al WebSocket
                await self.send(text_data=json.dumps({
                    'numerodeticker': turno['numerodeticker'],
                    'departamento': turno['departamento'],
                    'estado': turno['estado']
                }))
                print(f"Datos de turno {turno['numerodeticker']} enviados a cliente WebSocket")
            else:
                print(f"No se encontró información del turno ID: {turno_id}")
        
        except Exception as e:
            print(f"Error en recibir_llamado: {str(e)}")

    @database_sync_to_async
    def get_turno_info(self, turno_id):
        try:
            turno = Turnos.objects.select_related('departamento').get(pk=turno_id)
            return {
                'numerodeticker': turno.numerodeticker,
                'departamento': {
                    'nombre': turno.departamento.nombre,
                    'descripcion': turno.departamento.descripcion if hasattr(turno.departamento, 'descripcion') else "N/A"
                },
                'estado': turno.estado
            }
        except Turnos.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error al obtener datos del turno: {str(e)}")
            return None