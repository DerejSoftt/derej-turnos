import random
from django.contrib.sessions.backends.db import SessionStore  # Importación necesaria
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cliente
from .models import Departamento, Usuarios, Turnos
import json
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
import random
import string
import os  # Para la impresión
import logging
from django.views.decorators.http import require_POST
from escpos.printer import Usb
import time
from datetime import datetime,  timedelta
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from django.views.decorators.http import require_GET


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import pandas as pd
#from django.db import IntegrityError

from django.core.exceptions import PermissionDenied
from django.db import connection

# from django.template.loader import render_to_string

from django.conf import settings

#from io import BytesIO
#from reportlab.pdfgen import canvas
import pyttsx3

# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import mm
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import Paragraph, SimpleDocTemplate


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import time
import subprocess

import win32print
import win32api
import textwrap

from .voice_assistant import Command
import logging



# Create your views here.

# def index(request):
#     # Obtener todos los departamentos ordenados por nombre
#     departamentos = Departamento.objects.all().order_by('nombre')
#     context = {
#         'departamentos': departamentos
#     }
#     return render(request, 'system_turnos/index.html', context)



# def inicio(request):
#     if request.method == 'POST':
#         numero_cedula = request.POST.get('cedula')
        
#         turno = random.randint(1,100)
        
#         return render(request, 'system_turnos/turnos.html', {'turno': turno})
    
#     return render(request, 'system_turnos/inicio.html')


def index(request):
    """
    Vista para la selección de departamentos
    """
    departamentos = Departamento.objects.all().order_by('nombre')
    return render(request, 'system_turnos/index.html', {'departamentos': departamentos})

# def inicio(request, departamento_id=None):
#     """
#     Vista para el ingreso de cédula con modal para el turno
#     """
#     if departamento_id:
#         departamento = get_object_or_404(Departamento, pk=departamento_id)
#         return render(request, 'system_turnos/inicio.html', {'departamento': departamento})
    
#     return redirect('index')


# @csrf_exempt
# def verificar_cedula(request):
#     if request.method == 'POST':
#         try:
#             cedula = request.POST.get('cedula', '').strip()
#             departamento_id = request.POST.get('departamento_id', '').strip()

#             if not cedula or not departamento_id:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Cédula y departamento son requeridos'
#                 }, status=400)

#             # Obtener cliente
#             try:
#                 cliente = Cliente.objects.get(cedula=cedula)
#             except Cliente.DoesNotExist:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Cliente no registrado'
#                 }, status=404)

#             # Obtener departamento
#             try:
#                 departamento = Departamento.objects.get(pk=int(departamento_id))
#             except (Departamento.DoesNotExist, ValueError):
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Departamento no válido'
#                 }, status=400)

#             # Generar turno único con reintentos por si hay colisión
#             max_intentos = 5
#             intentos = 0
#             turno_creado = False
            
#             while not turno_creado and intentos < max_intentos:
#                 try:
#                     # Generar código de turno (2 letras + 3 números)
#                     letras = ''.join(random.choices(string.ascii_uppercase, k=2))
#                     numeros = ''.join(random.choices(string.digits, k=3))
#                     numerodeticker = f"{letras}{numeros}"
                    
#                     # Crear el turno
#                     turno = Turnos.objects.create(
#                         numerodeticker=numerodeticker,
#                         nombre=f"{cliente.nombre} {cliente.apellido}",
#                         cedula=cliente.cedula,
#                         departamento=departamento,
#                         estado='pendiente'
#                     )
#                     turno_creado = True
                    
#                 except IntegrityError:
#                     # Si hay duplicado, intentar con otro código
#                     intentos += 1
#                     continue
            
#             if not turno_creado:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'No se pudo generar un turno único después de varios intentos'
#                 }, status=500)

#             return JsonResponse({
#                 'status': 'success',
#                 'turno': numerodeticker,
#                 'departamento': departamento.nombre,
#                 'nombre': f"{cliente.nombre} {cliente.apellido}"
#             })

#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f'Error interno del servidor: {str(e)}'
#             }, status=500)

#     return JsonResponse({
#         'status': 'error',
#         'message': 'Método no permitido'
#     }, status=405)




# Configuración para impresión
# try:
#     import win32print
#     import win32api
#     USE_CUPS = False
# except ImportError:
#     try:
#         import cups
#         USE_CUPS = True
#     except ImportError:
#         print("Advertencia: No se encontraron bibliotecas de impresión. La impresión directa no funcionará.")
#         USE_CUPS = None


def inicio(request, departamento_id=None):
    """Vista principal para ingreso de cédula"""
    if departamento_id:
        departamento = get_object_or_404(Departamento, pk=departamento_id)
        return render(request, 'system_turnos/inicio.html', {'departamento': departamento})
    return redirect('index')

# def centrar_texto(texto, caracteres=32):
#     """Centra el texto para impresoras térmicas"""
#     texto = texto.strip()
#     espacios = (caracteres - len(texto)) // 2
#     espacios = max(0, espacios)
#     return " " * espacios + texto

# def generar_ticket_texto(turno, departamento, nombre):
#     """Genera el contenido del ticket como texto plano"""
#     return f"""
# {centrar_texto("SISTEMA DE TURNOS")}
# {centrar_texto("----------------------")}

# {centrar_texto(f"DEPTO: {departamento}")}
# {centrar_texto(f"CLIENTE: {nombre}")}

# {centrar_texto("----------------------")}
# {centrar_texto("TURNO:")}
# {centrar_texto(turno, caracteres=24)}

# {centrar_texto("----------------------")}
# {centrar_texto(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))}

# \n\n\n\x1B@\x1DV1  # Comandos para corte de papel
# """

# def imprimir_texto_crudo(contenido, printer_name="80mm Series Printer"):
#     """Envía texto directamente a la impresora térmica"""
#     try:
#         # Verificar impresoras disponibles
#         printers = [printer[2] for printer in win32print.EnumPrinters(
#             win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        
#         if printer_name not in printers:
#             raise Exception(f"Impresora '{printer_name}' no encontrada")
        
#         # Abrir la impresora
#         hprinter = win32print.OpenPrinter(printer_name)
        
#         try:
#             # Iniciar documento
#             win32print.StartDocPrinter(hprinter, 1, ("Ticket de Turno", None, "RAW"))
#             win32print.StartPagePrinter(hprinter)
            
#             # Enviar contenido
#             win32print.WritePrinter(hprinter, contenido.encode('utf-8'))
            
#             # Finalizar
#             win32print.EndPagePrinter(hprinter)
#             win32print.EndDocPrinter(hprinter)
#             return True
#         finally:
#             win32print.ClosePrinter(hprinter)
#     except Exception as e:
#         print(f"Error en impresión directa: {str(e)}")
#         return False


# def inicio(request, departamento_id=None):
#     """Vista principal para ingreso de cédula"""
#     if departamento_id:
#         departamento = get_object_or_404(Departamento, pk=departamento_id)
#         return render(request, 'system_turnos/inicio.html', {'departamento': departamento})
#     return redirect('index')

# def centrar_texto(texto, caracteres=32):
#     """Centra el texto para impresoras térmicas"""
#     texto = texto.strip()
#     espacios = (caracteres - len(texto)) // 2
#     espacios = max(0, espacios)
#     return " " * espacios + texto

# def generar_ticket_texto(turno, departamento, nombre):
#     """Genera el contenido del ticket como texto plano"""
#     return f"""
# {centrar_texto("SISTEMA DE TURNOS")}
# {centrar_texto("----------------------")}

# {centrar_texto(f"DEPTO: {departamento}")}
# {centrar_texto(f"CLIENTE: {nombre}")}

# {centrar_texto("----------------------")}
# {centrar_texto("TURNO:")}
# {centrar_texto(turno, caracteres=24)}

# {centrar_texto("----------------------")}
# {centrar_texto(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))}

# \n\n\n\x1B@\x1DV1  # Comandos para corte de papel
# """

# def imprimir_texto_crudo(contenido, printer_name="80mm Series Printer"):
#     """Envía texto directamente a la impresora térmica"""
#     try:
#         # Verificar impresoras disponibles
#         printers = [printer[2] for printer in win32print.EnumPrinters(
#             win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        
#         if printer_name not in printers:
#             raise Exception(f"Impresora '{printer_name}' no encontrada")
        
#         # Abrir la impresora
#         hprinter = win32print.OpenPrinter(printer_name)
        
#         try:
#             # Iniciar documento
#             win32print.StartDocPrinter(hprinter, 1, ("Ticket de Turno", None, "RAW"))
#             win32print.StartPagePrinter(hprinter)
            
#             # Enviar contenido
#             win32print.WritePrinter(hprinter, contenido.encode('utf-8'))
            
#             # Finalizar
#             win32print.EndPagePrinter(hprinter)
#             win32print.EndDocPrinter(hprinter)
#             return True
#         finally:
#             win32print.ClosePrinter(hprinter)
#     except Exception as e:
#         print(f"Error en impresión directa: {str(e)}")
#         return False

# def imprimir_ticket(turno, departamento, nombre):
#     """Función principal para imprimir tickets"""
#     try:
#         # Generar contenido del ticket
#         ticket_content = generar_ticket_texto(turno, departamento, nombre)
        
#         # Intentar impresión directa
#         if imprimir_texto_crudo(ticket_content):
#             return True
        
#         # Fallback: Método alternativo con comando COPY
#         try:
#             temp_file = os.path.join(os.getenv("TEMP"), f"ticket_{turno}.txt")
#             with open(temp_file, "w", encoding="utf-8") as f:
#                 f.write(ticket_content)
            
#             command = f'copy /B "{temp_file}" "\\\\DESKTOP-68MH80H\\80mm Series Printer"'
#             subprocess.run(command, shell=True, timeout=15)
#             return True
#         except Exception as e:
#             print(f"Error en método alternativo: {str(e)}")
#             return False
#     except Exception as e:
#         print(f"Error general al imprimir: {str(e)}")
#         return False


def imprimir_ticket(turno, departamento, nombre,  descripcion):
    """
    Imprime un ticket de turno sin abrir diálogos, con texto desplazado y tamaño aumentado.
    """
    try:
        # Configuración de la impresora
        PRINTER_NAME = "80mm Series Printer"
        ANCHO_IMPRESORA = 32  # Ancho típico para impresoras de 80mm
        
        # Obtener fecha y hora actuales
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        hora_actual = datetime.now().strftime('%H:%M:%S')
        
        # Función para desplazar texto
        def desplazar_texto(texto, espacios=0):
            return " " * espacios + str(texto).strip()
        
        # Crear contenido con mejor formato
        ticket_content = (
            "\x1B@"  # Reset completo de la impresora
            
            # Encabezado (centrado)
            "\x1B!\x38"  # Negrita y doble altura
            f"{desplazar_texto('SISTEMA DE TURNOS', 5)}\n"
            "\x1B!\x00"  # Restablecer formato
            f"{desplazar_texto('='*45, 2)}\n\n" # esta son las lineas que tienen los ticker
            
            # Número de turno (desplazado y aumentado)
            "\x1B!\x18"  # Doble altura (más grande que antes)
            f"{desplazar_texto('Su número de turno', 15)}\n\n\n"  # Añadidos 2 saltos de línea extra
            "\x1B!\x30"  # Doble altura y ancho (máximo tamaño)
            f"{desplazar_texto(turno, 10)}\n\n"
            "\x1B!\x00"  # Restablecer formato
            f"{desplazar_texto('-'*45, 2)}\n\n"
            
            # Información del cliente (desplazada y aumentada)
            "\x1B!\x08"  # Doble altura
            f"{desplazar_texto(f'Departamento: {departamento.upper()}', 5)}\n"
            f"{desplazar_texto(f'Cliente: {nombre.title()}', 5)}\n"
            f"{desplazar_texto(f'Destino: {descripcion.title()}', 5)}\n"
            "\x1B!\x00"  # Restablecer formato
            "\n"
            
            # Fecha y hora
            f"{desplazar_texto(f'Fecha: {fecha_actual}', 2)}\n"
            f"{desplazar_texto(f'Hora: {hora_actual}', 2)}\n\n"
            
            # Pie de página
            f"{desplazar_texto('Gracias por su visita', 4)}\n"
            f"{desplazar_texto('Por favor, espere a ser llamado', 1)}\n"
            
            # Corte de papel
            "\n\x1D\x56\x00"
        )
        
        # Enviar directamente a la impresora sin diálogos
        hprinter = win32print.OpenPrinter(PRINTER_NAME)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, ticket_content.encode('cp850', errors='replace'))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            return True
        finally:
            win32print.ClosePrinter(hprinter)
            
    except Exception as e:
        print(f"Error al imprimir: {str(e)}")
        return False

def centrar_texto(texto, ancho_total):
    """
    Centra exactamente el texto en el ancho especificado.
    """
    texto = texto.strip()
    if len(texto) >= ancho_total:
        return texto[:ancho_total]
    
    espacios = (ancho_total - len(texto)) // 2
    return " " * espacios + texto

def desplazar_texto(texto, ancho_total, espacios_extra=0):
    """
    Desplaza el texto a la derecha con espacios adicionales.
    
    Parámetros:
        texto: Texto a formatear
        ancho_total: Ancho máximo de la línea
        espacios_extra: Número de espacios adicionales para desplazar
    """
    texto = texto.strip()
    if len(texto) >= ancho_total:
        return texto[:ancho_total]
    
    return " " * espacios_extra + texto

def prueba_impresora():
    """Función para probar directamente la impresora"""
    test_content = (
        "\x1B@\x1B!\x08"  # Reset + negrita
        "PRUEBA DE IMPRESORA\n"
        "\x1B!\x00"       # Reset
        "----------------\n"
        "\x1B!\x10"       # Doble altura
        "TEST EXITOSO\n"
        "\x1B!\x00"       # Reset
        "----------------\n"
        "\x1DVA0"         # Cortar papel
    )
    
    try:
        hprinter = win32print.OpenPrinter("80mm Series Printer")
        win32print.StartDocPrinter(hprinter, 1, ("Test", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, test_content.encode('cp437'))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)
        print("Prueba enviada correctamente")
        return True
    except Exception as e:
        print(f"Error en prueba: {str(e)}")
        return False


@csrf_exempt
def verificar_cedula(request):
    """Endpoint completo para verificar cédula y generar turno"""
    if request.method == 'POST':
        try:
            # 1. Obtener y validar datos del formulario
            cedula = request.POST.get('cedula', '').strip()
            departamento_id = request.POST.get('departamento_id', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()

            # Validaciones básicas
            if not cedula or not departamento_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cédula y departamento son requeridos'
                }, status=400)

            if not cedula.isdigit() or len(cedula) != 11:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cédula no válida. Debe tener 11 dígitos'
                }, status=400)

            # 2. Buscar cliente en la base de datos
            try:
                cliente = Cliente.objects.get(cedula=cedula)
            except Cliente.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cliente no registrado'
                }, status=404)

            # 3. Verificar departamento
            try:
                departamento = Departamento.objects.get(pk=int(departamento_id))
                inicial = departamento.nombre[0].upper()
            except (Departamento.DoesNotExist, ValueError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Departamento no válido'
                }, status=400)

            # 4. Generar turno con formato DEPARTAMENTO + NÚMERO
            ultimo_turno = Turnos.objects.filter(
                departamento_id=departamento_id,
                numerodeticker__startswith=inicial
            ).order_by('-numerodeticker').first()
            
            if ultimo_turno:
                try:
                    numero = int(ultimo_turno.numerodeticker[len(inicial):]) + 1
                    nuevo_numero = f"{inicial}{numero}"
                except ValueError:
                    nuevo_numero = f"{inicial}1"
            else:
                nuevo_numero = f"{inicial}1"
            
            # Crear el turno
            turno = Turnos.objects.create(
                numerodeticker=nuevo_numero,
                nombre=f"{cliente.nombre} {cliente.apellido}",
                cedula=cliente.cedula,
                departamento=departamento,
                descripcion=descripcion,
                estado='pendiente'
            )

            # 5. Imprimir ticket
            impreso = imprimir_ticket(
                turno=nuevo_numero,
                departamento=departamento.nombre,
                nombre=f"{cliente.nombre} {cliente.apellido}",
                descripcion=descripcion
            )

            # 6. Retornar respuesta exitosa
            return JsonResponse({
                'status': 'success',
                'turno': nuevo_numero,
                'departamento': departamento.nombre,
                'nombre': f"{cliente.nombre} {cliente.apellido}",
                'descripcion': descripcion,
                'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'impreso': impreso
            })

        except Exception as e:
            import traceback
            print(f"Error en verificar_cedula: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)

def verificar_impresora():
    try:
        # Listar todas las impresoras disponibles
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        print("Impresoras disponibles:")
        for i, printer in enumerate(printers, 1):
            print(f"{i}. {printer[2]}")
        
        # Verificar conexión con la impresora específica
        PRINTER_NAME = "80mm Series Printer"
        if PRINTER_NAME in [p[2] for p in printers]:
            hprinter = win32print.OpenPrinter(PRINTER_NAME)
            win32print.ClosePrinter(hprinter)
            print(f"\n✅ La impresora '{PRINTER_NAME}' está conectada correctamente")
            return True
        else:
            print(f"\n❌ La impresora '{PRINTER_NAME}' no fue encontrada")
            return False
    except Exception as e:
        print(f"\n❌ Error al verificar impresora: {str(e)}")
        return False

def incrementar_letras(letras):
    """Incrementa letras en secuencia (AA->AB, AZ->BA, ZZ->AAA)"""
    letras = list(letras.upper())
    carry = True
    i = len(letras) - 1
    
    while carry and i >= 0:
        if letras[i] == 'Z':
            letras[i] = 'A'
            i -= 1
        else:
            letras[i] = chr(ord(letras[i]) + 1)
            carry = False
    
    if carry:
        letras.insert(0, 'A')
    
    return ''.join(letras)







# def turnos(request):
#     return render (request, 'system_turnos/turnos.html' )


def asignaciondp(request):
    return render (request, 'system_turnos/asignaciondp.html')


def clientes(request):
    if request.method == "POST":
        cedula = request.POST.get("cedula")
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")

        if not Cliente.objects.filter(cedula=cedula).exists():
            Cliente.objects.create(cedula=cedula, nombre=nombre, apellido=apellido)
            return JsonResponse({"mensaje": "Cliente agregado correctamente"}, status=200)
        else:
            return JsonResponse({"mensaje": "El cliente ya existe"}, status=400)

    return render(request, "system_turnos/clientes.html")



def guardar_cliente(request):
    if request.method == "POST":
        print(request.POST)  # 🔍 Ver qué llega en la solicitud

        cedula = request.POST.get("cedula", "").strip()
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()

        # Verificar si algún campo está vacío
        if not cedula or not nombre or not apellido:
            return JsonResponse({"mensaje": "Todos los campos son obligatorios"}, status=400)

        # Verificar si el cliente ya existe
        if Cliente.objects.filter(cedula=cedula).exists():
            return JsonResponse({"mensaje": "Este cliente ya está registrado"}, status=400)

        Cliente.objects.create(cedula=cedula, nombre=nombre, apellido=apellido)
        return JsonResponse({"mensaje": "Cliente agregado correctamente"})
    
    return JsonResponse({"error": "Método no permitido"}, status=405)




def departamentos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if data.get('action') == 'create':
                Departamento.objects.create(
                    nombre=data['nombre'],
                    ubicacion=data.get('ubicacion', ''),  # Usando get() con valor por defecto
                    descripcion=data.get('descripcion', '')  # Usando get() con valor por defecto
                )
                return JsonResponse({'success': True})
            
            elif data.get('action') == 'update':
                departamento = Departamento.objects.get(id=data['id'])
                departamento.nombre = data['nombre']
                departamento.ubicacion = data.get('ubicacion', '')
                departamento.descripcion = data.get('descripcion', '')
                departamento.save()
                return JsonResponse({'success': True})
            
            elif data.get('action') == 'delete':
                Departamento.objects.get(id=data['id']).delete()
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET request
    departamentos = list(Departamento.objects.all().values('id', 'nombre', 'ubicacion', 'descripcion'))
    return render(request, 'system_turnos/departamentos.html', {
        'departamentos_json': json.dumps(departamentos)
    })





def creacionuser(request):
    departamentos = Departamento.objects.all()
    usuarios = Usuarios.objects.select_related('departamento').all()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            cedula = request.POST.get('cedula')
            correo = request.POST.get('correo_electronico')
            usuario = request.POST.get('nombre_usuario')
            contrasena = request.POST.get('contrasena')
            departamento_id = request.POST.get('departamento')  # Cambiado a 'departamento'
            cargo = request.POST.get('cargo')  # Cambiado a 'cargo'
            
            print(f"Datos recibidos: {request.POST}")  # Para depuración
            
            # Validar que el departamento existe
            departamento = Departamento.objects.get(id=departamento_id)
            
            # Crear y guardar el usuario
            nuevo_usuario = Usuarios(
                nombre=nombre,
                apellido=apellido,
                cedula=cedula,
                correo_electronico=correo,
                nombre_usuario=usuario,
                contrasena=make_password(contrasena),
                departamento=departamento,
                cargo=cargo
            )
            nuevo_usuario.save()
            
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('creacionuser')
        
        except Departamento.DoesNotExist:
            messages.error(request, 'Departamento seleccionado no válido')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            print(f"Error: {str(e)}")  # Para depuración

    context = {
        'departamentos': departamentos,
        'usuarios': usuarios,
    }
    return render(request, 'system_turnos/creacionuser.html', context)


# def eliminar_usuario(request, user_id):
#     if request.method == 'POST':
#         try:
#             usuario = Usuarios.objects.get(id=user_id)
#             usuario.delete()
#             return JsonResponse({'success': True})
#         except Usuarios.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     return JsonResponse({'success': False, 'error': 'Método no permitido'})

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def delete_user(request, user_id):
    try:
        # Usar tu modelo Usuarios en lugar del User por defecto
        user = Usuarios.objects.get(id=user_id)
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario eliminado correctamente'
        })
        
    except Usuarios.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




@csrf_exempt
@require_http_methods(["POST"])
def update_user(request, user_id):
    try:
        data = json.loads(request.body)
        user = Usuarios.objects.get(id=user_id)
        
        # Actualizar campos básicos
        user.nombre = data.get('nombre', user.nombre)
        user.apellido = data.get('apellido', user.apellido)
        user.cedula = data.get('cedula', user.cedula)
        user.correo_electronico = data.get('correo_electronico', user.correo_electronico)
        user.nombre_usuario = data.get('nombre_usuario', user.nombre_usuario)
        
        # Actualizar contraseña si se proporcionó
        if 'contrasena' in data and data['contrasena']:
            user.contrasena = make_password(data['contrasena'])
        
        # Actualizar departamento si se proporciona
        if 'departamento' in data:
            user.departamento = Departamento.objects.get(id=data['departamento'])
        
        # Actualizar cargo si se proporciona
        if 'cargo' in data:
            user.cargo = data['cargo']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })
        
    except Usuarios.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=404)
    except Departamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Departamento no válido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




# def vistadeturnos(request):
#     query = request.GET.get('q', '')
#     estado = request.GET.get('estado', 'pendiente')  # Por defecto solo pendientes
    
#     # Consulta base - Orden ascendente por hora
#     turnos_list = Turnos.objects.all().order_by('hora')
    
#     # Filtrado principal
#     if estado == 'pendiente':
#         turnos_list = turnos_list.exclude(estado__in=['atendido', 'cancelado'])
#     elif estado in ['atendido', 'cancelado']:
#         turnos_list = turnos_list.filter(estado=estado)
#     # Si estado == 'todos' no aplicamos filtro adicional
    
#     # Búsqueda adicional
#     if query:
#         turnos_list = turnos_list.filter(
#             Q(numerodeticker__icontains=query) | 
#             Q(cedula__icontains=query)
#         )
    
#     paginator = Paginator(turnos_list, 10)
#     page_number = request.GET.get('page')
#     turnos = paginator.get_page(page_number)
    
#     context = {
#         'turnos': turnos,
#         'query': query,
#         'estado_seleccionado': estado
#     }
#     return render(request, 'system_turnos/vistadeturnos.html', context)


def vistadeturnos(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', 'pendiente')
    
    # Consulta base
    turnos_list = Turnos.objects.all()
    
    # Filtrado principal
    if estado == 'pendiente':
        turnos_list = turnos_list.exclude(estado__in=['atendido', 'cancelado'])
    elif estado in ['atendido', 'cancelado']:
        turnos_list = turnos_list.filter(estado=estado)
    
    # Búsqueda adicional
    if query:
        turnos_list = turnos_list.filter(
            Q(numerodeticker__icontains=query) | 
            Q(cedula__icontains=query))
    
    # Ordenar primero por departamento y luego por número de turno (numéricamente)
    turnos_list = turnos_list.select_related('departamento')
    
    # Ordenación personalizada para que los números se ordenen correctamente
    # Esto ahora maneja el formato D1, D2, D10 (donde D es la inicial del departamento)
    turnos_ordenados = sorted(turnos_list, 
        key=lambda t: (
            t.departamento.nombre, 
            int(t.numerodeticker[1:]) if t.numerodeticker[1:].isdigit() else 0
        ))
    
    # Paginar la lista ordenada manualmente
    paginator = Paginator(turnos_ordenados, 10)
    page_number = request.GET.get('page')
    turnos = paginator.get_page(page_number)
    
    context = {
        'turnos': turnos,
        'query': query,
        'estado_seleccionado': estado
    }
    return render(request, 'system_turnos/vistadeturnos.html', context)

def llamar_turno(request, ticket_id):
    try:
        turno = Turnos.objects.get(numerodeticker=ticket_id)
        turno.estado = 'llamando'
        turno.save()
        
        # Notificar a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "turnos",
            {
                "type": "turno_update",
                "data": {
                    "numerodeticker": turno.numerodeticker,
                    "estado": turno.estado,
                    "departamento": {
                        "nombre": turno.departamento.nombre,
                        "descripcion": turno.departamento.descripcion
                    },
                    "action": "llamar"  # Nueva propiedad para identificar la acción
                }
            }
        )
        return JsonResponse({'success': True})
    except Turnos.DoesNotExist:
        return JsonResponse({'error': 'Turno no encontrado'}, status=404)

def reporte(request):
    # Obtener el período seleccionado (por defecto semana)
    period = request.GET.get('period', 'week')
    
    # Calcular fechas según el período
    today = datetime.now().date()
    if period == 'day':
        start_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())  # Lunes de esta semana
    elif period == 'month':
        start_date = today.replace(day=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today - timedelta(days=today.weekday())  # Por defecto semana
    
    # Filtrar turnos por período
    turnos = Turnos.objects.filter(hora__date__gte=start_date)
    
    # Convertir a DataFrame de pandas
    df = pd.DataFrame.from_records(turnos.values(
        'id', 'numerodeticker', 'departamento__nombre', 'estado', 'hora'
    ))
    
    # Si hay datos, procesarlos
    if not df.empty:
        # Convertir hora a datetime
        df['hora'] = pd.to_datetime(df['hora'])
        
        # Contar turnos por departamento
        dept_counts = df['departamento__nombre'].value_counts().reset_index()
        dept_counts.columns = ['departamento', 'total']
        
        # Calcular porcentajes
        total_turnos = dept_counts['total'].sum()
        dept_counts['porcentaje'] = round((dept_counts['total'] / total_turnos) * 100, 1)
        
        # Ordenar por cantidad descendente
        dept_counts = dept_counts.sort_values('total', ascending=False)
        
        # Preparar datos para el gráfico
        labels = dept_counts['departamento'].tolist()
        data = dept_counts['total'].tolist()
        
        # Departamento más activo
        dept_mas_activo = dept_counts.iloc[0]['departamento']
        turnos_dept_mas_activo = dept_counts.iloc[0]['total']
        
        # Calcular promedio diario
        if period == 'day':
            avg_daily = total_turnos
        else:
            days = (today - start_date).days + 1
            avg_daily = round(total_turnos / days, 1)
        
        # Calcular cambio porcentual vs período anterior
        cambio_porcentual = calcular_cambio_porcentual(period, total_turnos)
    else:
        labels = []
        data = []
        dept_mas_activo = "N/A"
        turnos_dept_mas_activo = 0
        avg_daily = 0
        cambio_porcentual = 0
    
    context = {
        'period': period,
        'total_turnos': total_turnos if not df.empty else 0,
        'dept_mas_activo': dept_mas_activo,
        'turnos_dept_mas_activo': turnos_dept_mas_activo,
        'avg_daily': avg_daily,
        'cambio_porcentual': cambio_porcentual,
        'chart_labels': labels,
        'chart_data': data,
        'dept_counts': dept_counts.to_dict('records') if not df.empty else [],
    }
    
    return render(request, 'system_turnos/reporte.html', context)

def calcular_cambio_porcentual(period, current_total):
    """Calcula el cambio porcentual respecto al período anterior"""
    if not current_total or current_total == 0:
        return 0
    
    today = datetime.now().date()
    
    # Definir fechas del período anterior
    if period == 'day':
        start_prev = today - timedelta(days=1)
        end_prev = start_prev
    elif period == 'week':
        start_prev = today - timedelta(days=today.weekday() + 7)
        end_prev = start_prev + timedelta(days=6)
    elif period == 'month':
        start_prev = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_prev = today.replace(day=1) - timedelta(days=1)
    elif period == 'year':
        start_prev = today.replace(year=today.year-1, month=1, day=1)
        end_prev = today.replace(year=today.year-1, month=12, day=31)
    
    # Obtener total del período anterior
    prev_turnos = Turnos.objects.filter(
        hora__date__gte=start_prev,
        hora__date__lte=end_prev
    ).count()
    
    if prev_turnos == 0:
        return 100  # Si no había datos, consideramos crecimiento del 100%
    
    cambio = ((current_total - prev_turnos) / prev_turnos) * 100
    return round(cambio, 1)




""" 
def crear_turno(request):
    if request.method == 'POST':
        # ... tu lógica de creación ...
        nuevo_turno = Turnos.objects.create(...)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "turnos_global",
            {
                "type": "send.turno_update",
                "message": f"Turno {nuevo_turno.id} creado"
            }
        )
        return JsonResponse({"status": "success", "ticket": nuevo_turno.numerodeticker})
 """


# def crear_turno(request):
#     if request.method == 'POST':
#         # Obtener el último número de ticket para el departamento
#         departamento_id = request.POST.get('departamento')
#         ultimo_turno = Turnos.objects.filter(
#             departamento_id=departamento_id
#         ).order_by('-numerodeticker').first()
        
#         # Generar nuevo número de ticket
#         if ultimo_turno:
#             # Extraer la parte numérica del ticket (asumiendo formato "A001")
#             letra = ultimo_turno.numerodeticker[0]
#             numero = int(ultimo_turno.numerodeticker[1:]) + 1
#             nuevo_numero = f"{letra}{numero:03d}"
#         else:
#             # Primer ticket del departamento
#             departamento = Departamento.objects.get(id=departamento_id)
#             letra_inicial = departamento.nombre[0].upper()
#             nuevo_numero = f"{letra_inicial}001"
        
#         # Crear el nuevo turno
#         nuevo_turno = Turnos.objects.create(
#             numerodeticker=nuevo_numero,
#             departamento_id=departamento_id,
#             # ... otros campos ...
#         )
        
#         # Notificar a los clientes via WebSocket
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             "turnos_global",
#             {
#                 "type": "send.turno_update",
#                 "message": {
#                     "action": "nuevo_turno",
#                     "ticket": nuevo_numero,
#                     "departamento": nuevo_turno.departamento.nombre,
#                     "departamento_id": departamento_id
#                 }
#             }
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "ticket": nuevo_numero,
#             "departamento": nuevo_turno.departamento.nombre
#         })



def crear_turno(request):
    if request.method == 'POST':
        try:
            # Obtener el departamento seleccionado
            departamento_id = request.POST.get('departamento')
            departamento = Departamento.objects.get(id=departamento_id)
            
            # Obtener la inicial del departamento
            inicial = departamento.nombre[0].upper()
            
            # Obtener el último número de ticket para este departamento
            ultimo_turno = Turnos.objects.filter(
                departamento_id=departamento_id,
                numerodeticker__startswith=inicial
            ).order_by('-numerodeticker').first()
            
            # Generar nuevo número de ticket
            if ultimo_turno:
                # Extraer la parte numérica del ticket (ej: N1, N2, etc.)
                try:
                    # Eliminar la inicial para obtener solo el número
                    numero_texto = ultimo_turno.numerodeticker[len(inicial):]
                    numero = int(numero_texto) + 1
                    nuevo_numero = f"{inicial}{numero}"
                except ValueError:
                    # En caso de error, comenzamos con 1
                    nuevo_numero = f"{inicial}1"
            else:
                # Primer ticket del departamento
                nuevo_numero = f"{inicial}1"
            
            # Crear el nuevo turno
            nuevo_turno = Turnos.objects.create(
                numerodeticker=nuevo_numero,
                departamento_id=departamento_id,
                nombre=request.POST.get('nombre', ''),
                cedula=request.POST.get('cedula', ''),
                descripcion=request.POST.get('descripcion', ''),
                estado='pendiente'
            )
            
            # Notificar a los clientes via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "turnos_global",
                {
                    "type": "send.turno_update",
                    "message": {
                        "action": "nuevo_turno",
                        "ticket": nuevo_numero,
                        "departamento": nuevo_turno.departamento.nombre,
                        "departamento_id": departamento_id
                    }
                }
            )
            
            return JsonResponse({
                "status": "success",
                "ticket": nuevo_numero,
                "departamento": nuevo_turno.departamento.nombre
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)



@csrf_protect
def iniciosesion(request):
    if request.method == 'POST':
        # Cerrar cualquier sesión existente primero
        request.session.flush()
            
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            usuario = Usuarios.objects.get(nombre_usuario=username, activo=True)
            
            if usuario.check_password(password):
                # Crear nueva sesión con prefijo de departamento
                session_key = f"depto_{usuario.departamento.id}_user_{usuario.id}"
                new_session = SessionStore(session_key=session_key)
                new_session.create()
                
                # Configurar la nueva sesión
                request.session = new_session
                request.session['usuario_id'] = usuario.id
                request.session['departamento_id'] = usuario.departamento.id
                request.session['nombre_completo'] = f"{usuario.nombre} {usuario.apellido}"
                request.session['departamento_nombre'] = usuario.departamento.nombre
                
                # Configurar tiempo de sesión
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(0)
                
                request.session.save()
                
                # Configurar la cookie manualmente
                response = redirect('control')
                response.set_cookie(
                    'sessionid',
                    request.session.session_key,
                    max_age=1209600 if remember_me else None,
                    httponly=True,
                    secure=False,  # Cambiar a True en producción con HTTPS
                    samesite='Lax'
                )
                
                return response
                
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuarios.DoesNotExist:
            messages.error(request, 'Usuario no encontrado o inactivo')
    
    return render(request, 'system_turnos/iniciosesion.html')





def logout_view(request):
    if 'session_key' in request.session:
        # Eliminar la sesión específica de la base de datos
        from django.contrib.sessions.models import Session
        try:
            Session.objects.get(session_key=request.session['session_key']).delete()
        except Session.DoesNotExist:
            pass
            
    request.session.flush()
    return redirect('iniciosesion')

# def control(request):
#     # Verificar sesión
#     if 'usuario_id' not in request.session:
#         return redirect('iniciosesion')
    
#     try:
#         departamento_id = request.session['departamento_id']
        
#         # Obtener turnos del departamento del usuario
#         turnos_pendientes = Turnos.objects.filter(
#             departamento_id=departamento_id
#         ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
#         historial = Turnos.objects.filter(
#             departamento_id=departamento_id,
#             estado__in=['atendido', 'cancelado']
#         ).order_by('-hora')[:20]
        
#         context = {
#             'turnos_pendientes': turnos_pendientes,
#             'historial': historial,
#             'usuario': request.session.get('nombre_completo', 'Usuario'),
#             'departamento': request.session.get('departamento_nombre', 'Departamento')
#         }
        
#         return render(request, 'system_turnos/control.html', context)
        
#     except Exception as e:
#         messages.error(request, f"Error al cargar datos: {str(e)}")
#         return redirect('iniciosesion')



# def control(request):
#     # Verificar sesión
#     if 'usuario_id' not in request.session:
#         return redirect('iniciosesion')
    
#     try:
#         departamento_id = request.session['departamento_id']
        
#         # Obtener turnos del departamento del usuario
#         turnos_pendientes = Turnos.objects.filter(
#             departamento_id=departamento_id
#         ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
#         historial = Turnos.objects.filter(
#             departamento_id=departamento_id,
#             estado__in=['atendido', 'cancelado']
#         ).order_by('-hora')[:20]
        
#         context = {
#             'turnos_pendientes': turnos_pendientes,
#             'historial': historial,
#             'usuario': request.session.get('nombre_completo', 'Usuario'),
#             'departamento': request.session.get('departamento_nombre', 'Departamento')
#         }
        
#         return render(request, 'system_turnos/control.html', context)
        
#     except Exception as e:
#         messages.error(request, f"Error al cargar datos: {str(e)}")
#         return redirect('iniciosesion')


# @require_http_methods(["POST"])
# def actualizar_estado(request):
#     try:
#         if 'usuario_id' not in request.session:
#             return JsonResponse({'error': 'No autenticado'}, status=401)
            
#         data = json.loads(request.body)
#         turno_id = data.get('turno_id')
#         nuevo_estado = data.get('nuevo_estado')
        
#         if not turno_id or not nuevo_estado:
#             return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
#         turno = Turnos.objects.get(id=turno_id)
        
#         # Verificar que el turno pertenezca al departamento del usuario
#         if turno.departamento_id != request.session['departamento_id']:
#             return JsonResponse({'error': 'No autorizado para este departamento'}, status=403)
        
#         # Validar transición de estado
#         if nuevo_estado not in ['pendiente', 'llamado', 'atendido', 'cancelado']:
#             return JsonResponse({'error': 'Estado no válido'}, status=400)
        
#         # Actualizar estado
#         turno.estado = nuevo_estado
#         if nuevo_estado == 'atendido':
#             turno.atendido_por = Usuarios.objects.get(id=request.session['usuario_id'])
#         turno.save()
        
#         # Obtener listas actualizadas
#         turnos_pendientes = Turnos.objects.filter(
#             departamento_id=request.session['departamento_id']
#         ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
#         historial = Turnos.objects.filter(
#             departamento_id=request.session['departamento_id'],
#             estado__in=['atendido', 'cancelado']
#         ).order_by('-hora')[:20]
        
#         # Preparar respuesta
#         response_data = {
#             'success': True,
#             'turnos_pendientes': [{
#                 'id': t.id,
#                 'ticket': t.numerodeticker,
#                 'paciente': t.nombre,
#                 'cedula': t.cedula,
#                 'departamento': t.departamento.nombre,
#                 'hora': t.hora.strftime("%H:%M %p"),
#                 'estado': t.estado,
#                 'referencia': t.referencia or ''
#             } for t in turnos_pendientes],
#             'historial': [{
#                 'id': t.id,
#                 'ticket': t.numerodeticker,
#                 'paciente': t.nombre,
#                 'cedula': t.cedula,
#                 'departamento': t.departamento.nombre,
#                 'hora': t.hora.strftime("%H:%M %p"),
#                 'estado': t.estado,
#                 'atendido_por': t.atendido_por.nombre if t.atendido_por else ''
#             } for t in historial]
#         }
        
#         return JsonResponse(response_data)
        
#     except Turnos.DoesNotExist:
#         return JsonResponse({'error': 'Turno no encontrado'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)




# @require_http_methods(["GET"])
# def obtener_turnos(request):
#     try:
#         if 'usuario_id' not in request.session:
#             return JsonResponse({'error': 'No autenticado'}, status=401)
            
#         departamento_id = request.session['departamento_id']
        
#         turnos_pendientes = Turnos.objects.filter(
#             departamento_id=departamento_id
#         ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
#         historial = Turnos.objects.filter(
#             departamento_id=departamento_id,
#             estado__in=['atendido', 'cancelado']
#         ).order_by('-hora')[:20]
        
#         response_data = {
#             'turnos_pendientes': [{
#                 'id': t.id,
#                 'ticket': t.numerodeticker,  # Cambiar a t.ticket si es necesario
#                 'paciente': t.nombre,        # Cambiar a t.paciente si es necesario
#                 'cedula': t.cedula,
#                 'departamento': t.departamento.nombre,
#                 'hora': t.hora.strftime("%H:%M %p"),
#                 'estado': t.estado,
#                 'referencia': t.referencia or ''
#             } for t in turnos_pendientes],
#             'historial': [{
#                 'id': t.id,
#                 'ticket': t.numerodeticker,  # Cambiar a t.ticket si es necesario
#                 'paciente': t.nombre,        # Cambiar a t.paciente si es necesario
#                 'cedula': t.cedula,
#                 'departamento': t.departamento.nombre,
#                 'hora': t.hora.strftime("%H:%M %p"),
#                 'estado': t.estado
#             } for t in historial]
#         }
        
#         return JsonResponse(response_data)
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
    



def control(request):
    """Vista principal para el panel de control de turnos"""
    # Verificar sesión
    if 'usuario_id' not in request.session:
        return redirect('iniciosesion')
    
    # Contexto para la plantilla
    context = {
        'usuario': request.session.get('nombre_completo', 'Usuario'),
        'departamento': request.session.get('departamento_nombre', 'Departamento')
    }
    return render(request, 'system_turnos/control.html', context)




@require_http_methods(["GET"])
def obtener_turnos(request):
    """Endpoint para obtener los turnos en formato JSON"""
    try:
        # Verificar autenticación
        if 'usuario_id' not in request.session:
            return JsonResponse({'error': 'No autenticado'}, status=401)
            
        departamento_id = request.session['departamento_id']
        departamento = Departamento.objects.get(id=departamento_id)
        inicial = departamento.nombre[0].upper()
        
        # Obtener turnos pendientes del departamento
        turnos_pendientes = Turnos.objects.filter(
            departamento_id=departamento_id
        ).exclude(estado='atendido').exclude(estado='cancelado')
        
        # Ordenar los turnos pendientes correctamente (por la parte numérica)
        turnos_pendientes = sorted(
            turnos_pendientes,
            key=lambda t: int(t.numerodeticker[len(inicial):]) if t.numerodeticker[len(inicial):].isdigit() else 0
        )
        
        # Obtener historial reciente
        historial = Turnos.objects.filter(
            departamento_id=departamento_id,
            estado__in=['atendido', 'cancelado']
        ).order_by('-hora')[:20]
        
        # Preparar respuesta JSON
        response_data = {
            'turnos_pendientes': [{
                'id': t.id,
                'ticket': t.numerodeticker,
                'paciente': t.nombre,
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado,
                'referencia': t.descripcion or ''
            } for t in turnos_pendientes],
            'historial': [{
                'id': t.id,
                'ticket': t.numerodeticker,
                'paciente': t.nombre,
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado,
                'atendido_por': t.atendido_por.nombre if t.atendido_por else ''
            } for t in historial]
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@require_http_methods(["POST"])
def actualizar_estado(request):
    """Endpoint para actualizar el estado de un turno"""
    try:
        # Verificar autenticación
        if 'usuario_id' not in request.session:
            return JsonResponse({'error': 'No autenticado'}, status=401)
            
        # Parsear datos JSON
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        nuevo_estado = data.get('nuevo_estado')
        
        # Validar datos requeridos
        if not turno_id or not nuevo_estado:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        # Obtener el turno
        turno = Turnos.objects.get(id=turno_id)
        
        # Verificar que el turno pertenezca al departamento del usuario
        if turno.departamento_id != request.session['departamento_id']:
            return JsonResponse({'error': 'No autorizado para este departamento'}, status=403)
        
        # Validar transición de estado
        if nuevo_estado not in ['pendiente', 'llamado', 'atendido', 'cancelado']:
            return JsonResponse({'error': 'Estado no válido'}, status=400)
        
        # Actualizar estado del turno
        turno.estado = nuevo_estado
        if nuevo_estado == 'atendido':
            turno.atendido_por = Usuarios.objects.get(id=request.session['usuario_id'])
        turno.save()
        
        # Obtener datos actualizados para la respuesta
        departamento_id = request.session['departamento_id']
        turnos_pendientes = Turnos.objects.filter(
            departamento_id=departamento_id
        ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
        historial = Turnos.objects.filter(
            departamento_id=departamento_id,
            estado__in=['atendido', 'cancelado']
        ).order_by('-hora')[:20]
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'turnos_pendientes': [{
                'id': t.id,
                'ticket': t.numerodeticker,
                'paciente': t.nombre,
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado,
                'referencia': t.descripcion or ''
            } for t in turnos_pendientes],
            'historial': [{
                'id': t.id,
                'ticket': t.numerodeticker,
                'paciente': t.nombre,
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado,
                'atendido_por': t.atendido_por.nombre if t.atendido_por else ''
            } for t in historial]
        }
        
        return JsonResponse(response_data)
        
    except Turnos.DoesNotExist:
        return JsonResponse({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def administracion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('reporte')  # Asegúrate que 'reporte' sea el nombre de tu URL
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'system_turnos/administracion.html')




def mantenimiento(request):
    return render(request, 'system_turnos/mantenimiento.html')
   


@csrf_exempt
@require_POST
def verificar_superusuario(request):
    """Verifica las credenciales del superusuario"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return JsonResponse({
                'success': True, 
                'nombre': user.get_full_name() or user.username
            })
        return JsonResponse({
            'success': False, 
            'error': 'Credenciales inválidas o usuario no es superadministrador'
        }, status=401)
    
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_POST
def limpiar_turnos(request):
    """Elimina turnos según los parámetros recibidos"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise PermissionDenied("Acceso denegado")
    
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        
        if tipo == 'all':
            Turnos.objects.all().delete()
            message = "Todos los turnos han sido eliminados"
        elif tipo == 'old':
            fecha = data.get('fecha')
            Turnos.objects.filter(hora__lt=fecha).delete()
            message = f"Turnos anteriores a {fecha} eliminados"
        elif tipo == 'status':
            estado = data.get('estado')
            Turnos.objects.filter(estado=estado).delete()
            message = f"Turnos con estado {estado} eliminados"
        else:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de limpieza no válido'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




@require_GET
def obtener_estadisticas_turnos(request):
    try:
        from django.db import connection
        table_name = Turnos._meta.db_table  # Obtiene el nombre real de la tabla
        
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    estado, 
                    COUNT(*) as total 
                FROM {table_name} 
                GROUP BY estado
            """)
            rows = cursor.fetchall()
            
            # Procesar resultados
            stats = {
                'pendiente': 0,
                'atendido': 0,
                'cancelado': 0
            }
            
            for estado, total in rows:
                stats[estado] = total
            
            # Obtener total general
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_general = cursor.fetchone()[0]
            
            return JsonResponse({
                'success': True,
                'total': total_general,
                'pendientes': stats['pendiente'],
                'atendidos': stats['atendido'],
                'cancelados': stats['cancelado']
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    






def turnos_llamados(request):
    turnos = Turnos.objects.filter(estado='llamado').select_related('departamento')
    data = [{
        'numerodeticker': t.numerodeticker,
        'departamento': {
            'nombre': t.departamento.nombre,
            'descripcion': t.departamento.descripcion
        },
        'estado': t.estado
    } for t in turnos]
    return JsonResponse(data, safe=False)