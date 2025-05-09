from django.core.management.base import BaseCommand
import time
import threading
import logging
import pyttsx3

from system_turnos.models import Turnos



class Command(BaseCommand):
    help = 'Inicia un asistente de voz para llamar turnos en estado "llamado"'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.engine = None
        self.ultimo_anuncio = None
        self.turnos_anunciados = set()
        self.lock = threading.Lock()
        self.interval = 5  # Segundos entre cada comprobación

    def setup_voice(self):
        """Configura la voz para que use español si está disponible."""
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        
        # Busca voz en español
        for voice in voices:
            if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                self.stdout.write(self.style.SUCCESS(f"Voz en español seleccionada: {voice.name}"))
                break
        
        # Configura la velocidad y volumen
        self.engine.setProperty('rate', 150)  # Velocidad normal
        self.engine.setProperty('volume', 0.9)  # Volumen alto pero no máximo

    def anunciar_turno(self, turno):
        """Anuncia un turno por voz."""
        with self.lock:
            # Evita anunciar el mismo turno dos veces consecutivas
            if self.ultimo_anuncio == turno.numerodeticker:
                return False
            
            # Evita anunciar turnos ya anunciados recientemente
            if turno.id in self.turnos_anunciados:
                return False
            
            try:
                # Formato del mensaje
                mensaje = f"Turno {turno.numerodeticker}, favor acercarse a {turno.departamento.nombre}"
                self.stdout.write(f"Anunciando: {mensaje}")
                
                # Reproduce el mensaje
                self.engine.say(mensaje)
                self.engine.runAndWait()
                
                # Actualiza el seguimiento
                self.ultimo_anuncio = turno.numerodeticker
                self.turnos_anunciados.add(turno.id)
                
                # Programa la eliminación del turno de la lista de anunciados después de 2 minutos
                threading.Timer(120, lambda: self.turnos_anunciados.discard(turno.id)).start()
                
                return True
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error al anunciar turno {turno.numerodeticker}: {str(e)}"))
                return False

    def verificar_turnos(self):
        """Verifica los turnos en estado 'llamado' y los anuncia."""
        try:
            # Consulta turnos en estado "llamado"
            turnos_llamados = Turnos.objects.filter(estado='llamado').select_related('departamento')
            
            if turnos_llamados:
                self.stdout.write(f"Turnos encontrados en estado 'llamado': {len(turnos_llamados)}")
            
            # Anuncia cada turno
            for turno in turnos_llamados:
                self.anunciar_turno(turno)
                
                # Pequeña pausa entre anuncios si hay varios
                time.sleep(0.5)
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error al verificar turnos: {str(e)}"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando asistente de voz para turnos...'))
        self.setup_voice()
        
        try:
            while self.running:
                self.verificar_turnos()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Asistente de voz detenido por el usuario"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error en el bucle principal: {str(e)}"))
        finally:
            self.stdout.write(self.style.SUCCESS("Asistente de voz finalizado"))
