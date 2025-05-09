# # system_turnos/voice_announcer.py
# import pyttsx3
# from .models import Turnos
# from django.conf import settings
# import threading

# class VoiceAnnouncer:
#     def __init__(self):
#         self.engine = self.init_engine()
#         self.lock = threading.Lock()
        
#     def init_engine(self):
#         engine = pyttsx3.init()
        
#         # Configuración de voz (ajustable)
#         engine.setProperty('rate', 150)  # Velocidad (palabras por minuto)
#         engine.setProperty('volume', 1.0)  # Volumen (0.0 a 1.0)
        
#         # Intentar encontrar voz en español
#         voices = engine.getProperty('voices')
#         spanish_voice = next((v for v in voices if 'spanish' in v.name.lower() or 'es' in v.id.lower()), None)
#         if spanish_voice:
#             engine.setProperty('voice', spanish_voice.id)
        
#         return engine
    
#     def announce_turn(self, turno):
#         """Anuncia un turno específico"""
#         with self.lock:
#             message = f"Turno {turno.numerodeticker}, por favor acérquese al {turno.departamento.nombre}"
#             self.engine.say(message)
#             self.engine.runAndWait()
    
#     def check_pending_announcements(self):
#         """Verifica y anuncia turnos en estado 'llamando'"""
#         turnos_llamando = Turnos.objects.filter(estado='llamando')
        
#         for turno in turnos_llamando:
#             self.announce_turn(turno)
#             # Opcional: cambiar el estado después de anunciar
#             turno.estado = 'en_atencion'
#             turno.save()

# # Singleton para el anunciador
# announcer = VoiceAnnouncer()