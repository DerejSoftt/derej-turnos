import random
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
from datetime import datetime 
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect




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

def inicio(request, departamento_id=None):
    """
    Vista para el ingreso de cédula con modal para el turno
    """
    if departamento_id:
        departamento = get_object_or_404(Departamento, pk=departamento_id)
        return render(request, 'system_turnos/inicio.html', {'departamento': departamento})
    
    return redirect('index')






@csrf_exempt
def verificar_cedula(request):
    """
    Vista API para verificación de cédula y generación de turno
    """
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        departamento_id = request.POST.get('departamento_id', '').strip()
        
        if not cedula or not departamento_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Cédula y departamento son requeridos'
            }, status=400)
        
        try:
            departamento = Departamento.objects.get(pk=int(departamento_id))
            
            try:
                cliente = Cliente.objects.get(cedula=cedula)
                
                # Generar turno único (2 letras + 3 números)
                letras = random.choices(string.ascii_uppercase, k=2)
                numeros = random.choices(string.digits, k=3)
                turno = ''.join(letras + numeros)
                
                # Crear y guardar el turno - no incluir idcliente porque no existe en el modelo
                Turnos.objects.create(
                    numerodeticker=turno,
                    nombre=f"{cliente.nombre} {cliente.apellido}",
                    cedula=cliente.cedula,
                    departamento=departamento,
                    estado='pendiente'
                )
                
                return JsonResponse({
                    'status': 'success',
                    'turno': turno,
                    'departamento': departamento.nombre,
                    'nombre': f"{cliente.nombre} {cliente.apellido}"
                })
                
            except Cliente.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Usted no está registrado en nuestra base de datos'
                }, status=404)
                
        except Departamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Departamento no válido'
            }, status=404)
            
        except Exception as e:
            # Imprime el error en la consola para diagnóstico
            import traceback
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            
            return JsonResponse({
                'status': 'error',
                'message': f'Error al procesar su solicitud: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)




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






def vistadeturnos(request):
    # Obtener parámetros de búsqueda y filtrado
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', 'todos')
    
    # Consulta base - Orden ascendente por hora (más antiguos primero)
    turnos_list = Turnos.objects.all().order_by('hora')
    
    # Aplicar filtros
    if query:
        turnos_list = turnos_list.filter(
            Q(numerodeticker__icontains=query) | 
            Q(cedula__icontains=query)
        )
    
    if estado != 'todos':
        turnos_list = turnos_list.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(turnos_list, 10)  # 10 turnos por página
    page_number = request.GET.get('page')
    turnos = paginator.get_page(page_number)
    
    context = {
        'turnos': turnos,
        'query': query,
        'estado_seleccionado': estado
    }
    return render(request, 'system_turnos/vistadeturnos.html', context)



def reporte(request):
    return render (request, 'system_turnos/reporte.html')




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
    



@csrf_protect
def iniciosesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            usuario = Usuarios.objects.get(nombre_usuario=username, activo=True)
            
            if usuario.check_password(password):
                request.session['usuario_id'] = usuario.id
                request.session['departamento_id'] = usuario.departamento.id
                request.session['nombre_completo'] = f"{usuario.nombre} {usuario.apellido}"
                request.session['departamento_nombre'] = usuario.departamento.nombre
                
                return redirect('control')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuarios.DoesNotExist:
            messages.error(request, 'Usuario no encontrado o inactivo')
    
    return render(request, 'system_turnos/iniciosesion.html')

def logout_view(request):
    request.session.flush()
    return redirect('iniciosesion')

def control(request):
    # Verificar sesión
    if 'usuario_id' not in request.session:
        return redirect('iniciosesion')
    
    try:
        departamento_id = request.session['departamento_id']
        
        # Obtener turnos del departamento del usuario
        turnos_pendientes = Turnos.objects.filter(
            departamento_id=departamento_id
        ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
        historial = Turnos.objects.filter(
            departamento_id=departamento_id,
            estado__in=['atendido', 'cancelado']
        ).order_by('-hora')[:20]
        
        context = {
            'turnos_pendientes': turnos_pendientes,
            'historial': historial,
            'usuario': request.session.get('nombre_completo', 'Usuario'),
            'departamento': request.session.get('departamento_nombre', 'Departamento')
        }
        
        return render(request, 'system_turnos/control.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar datos: {str(e)}")
        return redirect('iniciosesion')

@require_http_methods(["POST"])
def actualizar_estado(request):
    try:
        if 'usuario_id' not in request.session:
            return JsonResponse({'error': 'No autenticado'}, status=401)
            
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        nuevo_estado = data.get('nuevo_estado')
        
        if not turno_id or not nuevo_estado:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        turno = Turnos.objects.get(id=turno_id)
        
        # Verificar que el turno pertenezca al departamento del usuario
        if turno.departamento_id != request.session['departamento_id']:
            return JsonResponse({'error': 'No autorizado para este departamento'}, status=403)
        
        # Validar transición de estado
        if nuevo_estado not in ['pendiente', 'llamado', 'atendido', 'cancelado']:
            return JsonResponse({'error': 'Estado no válido'}, status=400)
        
        # Actualizar estado
        turno.estado = nuevo_estado
        if nuevo_estado == 'atendido':
            turno.atendido_por = Usuarios.objects.get(id=request.session['usuario_id'])
        turno.save()
        
        # Obtener listas actualizadas
        turnos_pendientes = Turnos.objects.filter(
            departamento_id=request.session['departamento_id']
        ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
        historial = Turnos.objects.filter(
            departamento_id=request.session['departamento_id'],
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
                'referencia': t.referencia or ''
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




@require_http_methods(["GET"])
def obtener_turnos(request):
    try:
        if 'usuario_id' not in request.session:
            return JsonResponse({'error': 'No autenticado'}, status=401)
            
        departamento_id = request.session['departamento_id']
        
        turnos_pendientes = Turnos.objects.filter(
            departamento_id=departamento_id
        ).exclude(estado='atendido').exclude(estado='cancelado').order_by('hora')
        
        historial = Turnos.objects.filter(
            departamento_id=departamento_id,
            estado__in=['atendido', 'cancelado']
        ).order_by('-hora')[:20]
        
        response_data = {
            'turnos_pendientes': [{
                'id': t.id,
                'ticket': t.numerodeticker,  # Cambiar a t.ticket si es necesario
                'paciente': t.nombre,        # Cambiar a t.paciente si es necesario
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado,
                'referencia': t.referencia or ''
            } for t in turnos_pendientes],
            'historial': [{
                'id': t.id,
                'ticket': t.numerodeticker,  # Cambiar a t.ticket si es necesario
                'paciente': t.nombre,        # Cambiar a t.paciente si es necesario
                'cedula': t.cedula,
                'departamento': t.departamento.nombre,
                'hora': t.hora.strftime("%H:%M %p"),
                'estado': t.estado
            } for t in historial]
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)