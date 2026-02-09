![Logotipo de la aplicación](img-doc/derejturnos.png)

# Documentación Técnica de DerejTurnos

## 1. Introducción

**DerejTurnos** es una plataforma para la gestión de turnos, clientes y departamentos, orientada a entornos de atención presencial (oficinas, clínicas, comercios, etc.). Permite la asignación, control y visualización de turnos, impresión de tickets, administración de usuarios y departamentos, y reportes analíticos. Está desarrollada sobre **Django 4.2.20**, empleando **MySQL** como motor relacional principal y una única app denominada `system_turnos` que centraliza modelos, vistas, plantillas y recursos estáticos del sistema.

## 2. Tecnologías y dependencias clave

- **Django 4.2.20** (framework web y ORM)
- **MySQL** (motor relacional, configurable por variables de entorno)
- **Channels** para WebSockets y notificaciones en tiempo real
- **WhiteNoise** para servir archivos estáticos
- **python-dotenv** para variables de entorno
- **ReportLab** y **pyttsx3** para impresión y voz
- **Pandas** para reportes analíticos
- **Impresión térmica**: soporte para impresoras Windows y Linux

Ver [requirements.txt](turnos/requirements.txt) para la lista completa.

## 3. Arquitectura general

- **App principal:** `system_turnos` (modelos, vistas, templates, rutas)
- **Templates:** organizados en `system_turnos/templates/system_turnos/` para cada funcionalidad
- **Recursos estáticos:** en `static/` y `staticfiles/` (estilos, imágenes, sonidos)
- **Configuración central:** en [settings.py](turnos/turnos/settings.py)
- **Seguridad:** autenticación estándar Django, CSRF, permisos y roles

## Estructura de Carpetas

```
turnos/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── media/
│   └── tickets/
├── static/
│   └── sounds/
│   └── system_turnos/
│       └── estilos.css
├── system_turnos/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── voice_announcer.py
│   ├── voice_assistant.py
│   ├── migrations/
│   └── templates/
│       └── system_turnos/
│           ├── administracion.html
│           ├── asignaciondp.html
│           ├── clientes.html
│           ├── control.html
│           ├── creacionuser.html
│           ├── departamentos.html
│           ├── index.html
│           ├── inicio.html
│           ├── iniciosesion.html
│           ├── mantenimiento.html
│           ├── reporte.html
│           ├── vistadeturnos.html
└── turnos/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
```

## 4. Modelo de datos principal

Los modelos residen en [models.py](turnos/system_turnos/models.py):

| Modelo         | Rol principal                                                          | Relacionamientos destacados                |
| -------------- | ---------------------------------------------------------------------- | ------------------------------------------ |
| `Cliente`      | Registro de clientes (cédula, nombre, apellido)                        | Usado por `Turnos`                         |
| `Departamento` | Gestión de departamentos (nombre, ubicación, descripción)              | Usado por `Turnos`, `Usuarios`             |
| `Usuarios`     | Administración de usuarios (nombre, cargo, departamento, credenciales) | FK a `Departamento`                        |
| `Turnos`       | Control de turnos (ticket, cliente, departamento, estado, hora)        | FK a `Cliente`, `Departamento`, `Usuarios` |

## 5. Módulos funcionales

### 5.1 Autenticación y roles

- Login y logout con Django
- Creación, edición y eliminación de usuarios
- Roles por departamento y cargo

### 5.2 Gestión de turnos

- Asignación de turnos por departamento
- Validación de cédula y cliente
- Impresión de ticket (Windows/Linux)
- Visualización de turnos por estado (pendiente, llamado, atendido, cancelado)
- Llamado de turnos con notificación por voz (WebSockets y síntesis de voz)

### 5.3 Administración de departamentos

- Alta, edición y eliminación de departamentos
- Visualización y gestión desde panel

### 5.4 Gestión de clientes

- Registro y consulta de clientes
- Validación de duplicados

### 5.5 Reportes y analítica

- Reporte de turnos por período (día, semana, mes, año)
- Métricas: total, departamento más activo, promedio diario, cambio porcentual
- Visualización gráfica y exportación

### 5.6 Templates principales

- `index.html`: selector de departamentos
- `inicio.html`: ingreso de cédula y generación de turno
- `vistadeturnos.html`: visualización completa de turnos por departamento
- `clientes.html`: gestión de clientes
- `departamentos.html`: gestión de departamentos
- `creacionuser.html`: gestión de usuarios
- `reporte.html`: reportes analíticos

## 6. Flujo operativo end-to-end

1. **Selección de departamento**: usuario elige el área de atención
2. **Ingreso de cédula**: validación y registro de cliente
3. **Generación de turno**: asignación de ticket, impresión y notificación
4. **Visualización de turnos**: panel para operadores y clientes
5. **Llamado de turno**: notificación por voz y actualización de estado
6. **Reportes**: consulta de métricas y exportación

## 7. Integraciones internas y archivos relevantes

- **Rutas:** centralizadas en [urls.py](turnos/system_turnos/urls.py)
- **Templates:** cada feature tiene su HTML
- **Assets:** imágenes, sonidos y estilos en `static/`

## 8. Seguridad y cumplimiento

- Credenciales y llaves en `.env` (no versionado)
- CSRF habilitado globalmente
- Validaciones server-side para cédula, duplicados y permisos
- Soft delete en usuarios

## 9. Despliegue y configuración

1. Crear archivo `.env` con variables:

```bash
SECRET_KEY="tu_clave_secreta"
DB_NAME="nombre_base_datos"
DB_USER="usuario"
DB_PASSWORD="contraseña"
DB_HOST="localhost"
DB_PORT="3306"
ALLOWED_HOSTS="localhost,127.0.0.1"
CSRF_TRUSTED_ORIGINS="http://localhost,http://127.0.0.1"
DEBUG=True
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones:

```bash
python manage.py migrate
```

4. Crear superusuario:

```bash
python manage.py createsuperuser
```

5. Colectar estáticos:

```bash
python manage.py collectstatic
```

6. Ejecutar servidor:

```bash
python manage.py runserver
```

## 10. Métricas y mejoras futuras sugeridas

- **KPI adicionales:** tiempo de atención, rotación por departamento
- **Alertas proactivas:** notificaciones por WhatsApp o email
- **API pública:** endpoints REST para integraciones externas
- **Pruebas automatizadas:** ampliar [tests.py](turnos/system_turnos/tests.py)

---

## Modelos Clave

- **Cliente:** cédula, nombre, apellido
- **Departamento:** nombre, ubicación, descripción
- **Usuarios:** nombre, cargo, departamento, credenciales
- **Turnos:** ticket, cliente, departamento, estado, hora

## Templates

- `index.html`: selector de departamentos
- `inicio.html`: ingreso de cédula y generación de turno
- `vistadeturnos.html`: panel de turnos
- `clientes.html`: gestión de clientes
- `departamentos.html`: gestión de departamentos
- `creacionuser.html`: gestión de usuarios
- `reporte.html`: reportes analíticos

## Instalación

1. **Requisitos:**
   - Python 3.10+
   - Django 4.2.20
   - MySQL
   - Paquetes: `channels`, `mysqlclient`, `pillow`, `reportlab`, `asgiref`, `pandas`, `tzdata`, `pyttsx3`, `python-dotenv`, `whitenoise`

2. **Instalación de dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración de base de datos:**
   - Edita `.env` para definir `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

4. **Migraciones:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Creación de superusuario:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecución del servidor:**
   ```bash
   python manage.py runserver
   ```

## Uso

- Accede al sistema en `http://localhost:8000`
- Selecciona departamento y genera turno
- Visualiza turnos, clientes y reportes
- Administra usuarios y departamentos

## Seguridad y Roles

- Autenticación y autorización basada en usuarios y departamentos
- Roles por cargo y permisos

## Pruebas

- [tests.py](turnos/system_turnos/tests.py) preparado para pruebas unitarias

## Personalización

- Templates adaptables para branding propio
- Ampliación de modelos y vistas para nuevas funcionalidades

## Configuración

- Variables de entorno para seguridad y base de datos
- Soporte para archivos estáticos y media
- Configuración de zona horaria

## Contacto y Soporte

Para soporte, contactar al desarrollador o consultar la documentación de Django.

---
