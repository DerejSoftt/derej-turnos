from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.


# class Departamento(models.Model):
#     nombre = models.CharField(max_length=100, unique=True)
#     referencia = models.TextField(blank=True, null=True)
#     encargado = models.CharField(max_length=100)

#     def __str__(self):
#         return self.nombre


class Cliente(models.Model):
    cedula = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
  
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    



# class Turnos(models.Model):
#     idcliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
#     numerodeticker = models.CharField(max_length=10, unique=True)
#     nombre = models.CharField(max_length=100)
#     cedula = models.CharField(max_length=11)
#     departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
#     referencia = models.TextField(blank=True, null=True)
#     hora = models.DateTimeField(auto_now_add=True)
#     estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('atendido', 'Atendido'), ('cancelado', 'Cancelado')])

#     def __str__(self):
#         return f"Turno {self.numerodeticker} - {self.nombre} ({self.estado})"




# class Usuarios(models.Model):
#     nombre = models.CharField(max_length=100)
#     apellido = models.CharField(max_length=100)
#     cedula = models.CharField(max_length=11, unique=True)
#     correo_electronico = models.EmailField(unique=True)
#     nombre_usuario = models.CharField(max_length=50, unique=True)
#     contrasena = models.CharField(max_length=128)  # Se recomienda usar Django's auth para manejar contraseñas
#     departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
#     cargo = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.nombre} {self.apellido} ({self.cargo})"




class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    
    def __str__(self):
        return self.nombre

class Usuarios(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=11, unique=True)
    correo_electronico = models.EmailField(unique=True)
    nombre_usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=128)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cargo})"
    
    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

class Turnos(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('llamado', 'Llamado'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
    ]
    
    numerodeticker = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=11)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    referencia = models.CharField(max_length=300, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    hora = models.DateTimeField(auto_now_add=True)
    atendido_por = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Turno {self.numerodeticker} - {self.nombre}"