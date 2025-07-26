# 03. Estructura del Proyecto - INSERF

Este documento describe la organización de carpetas y módulos del backend de INSERF, basado en Django. Se busca mantener una estructura limpia, escalable y alineada con buenas prácticas.

---

## Vista General

```

inserf/
├── core/                # Modelos de dominio comunes: productos, órdenes, clientes
├── dashboard/           # Lógica de administración interna y vistas protegidas
├── landing/             # Vistas públicas y cliente final: login, home, pedidos
├── inserf/              # Configuración principal del proyecto Django (settings, urls)
├── manage.py            # Script de entrada para comandos Django

```

---

## Descripción por Carpeta

### `core/`

Contiene los modelos centrales de negocio y relaciones clave:

- `models.py`: Entidades como `Product`, `ProductVariant`, `Client`, `PurchaseOrder`, `OrderItem`.
- `admin.py`: Registro de modelos en el panel administrativo de Django.
- `tests.py`: Pruebas unitarias base para modelos del dominio.

### `dashboard/`

Contiene vistas protegidas y lógica de administración para el equipo interno:

- `views.py`: Vistas para el panel administrativo (`admin_home`, `list_clients`).
- `urls.py`: Rutas internas de la app administrativa (`/admin-panel/`).
- `fixtures/`: Datos de prueba para usuarios, clientes, productos y órdenes.
- `templates/dashboard/`: HTMLs para dashboard, sidebar y paneles.

### `landing/`

Contiene la lógica de la interfaz pública y autenticación:

- `views.py`: Vistas públicas como `home`, `login`, `my_orders`.
- `urls.py`: Rutas principales del sitio (`/`, `/login`, `/my-orders`).
- `templates/landing/`: HTML base y vistas del cliente.
- `templates/registration/`: Login personalizado.
- `static/`: Archivos CSS e imágenes del sitio web.

### `inserf/`

Configuración raíz del proyecto:

- `settings.py`: Configuraciones de Django (apps, bases de datos, templates, seguridad).
- `urls.py`: Rutas globales del proyecto.
- `wsgi.py`: Configuración para despliegue en servidores WSGI.
- `asgi.py`: Configuración para despliegue ASGI (opcional).

---

## Convenciones

- Separación clara entre lógica del cliente (`landing/`) y lógica del staff (`dashboard/`).
- Modelos compartidos en `core/`, accesibles desde ambas interfaces.
- Archivos de configuración y entrada de Django contenidos en `inserf/`.
- Uso de rutas con `app_name` y nombres explícitos (`landing:my_orders`, `dashboard:list_clients`).

---

## Siguientes Pasos

- Agregar carpeta `api/` si se define una API REST o GraphQL para clientes externos.
- Agregar carpeta `security/` si se modulariza la autenticación personalizada.
- Documentar dependencias externas y estructura de datos si se expone integración con terceros.
