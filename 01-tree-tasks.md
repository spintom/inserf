# 01. Árbol de Tareas Backend - INSERF (Django + PostgreSQL)

## 1. Configuración Inicial del Proyecto

- [X] `BE-01`: Inicializar proyecto Django con estructura base
- [X] `BE-02`: Crear app `core` con modelos base (`User`, `Client`, etc.)
- [X] `BE-03`: Configurar `settings.py` con `STATICFILES`, `AUTH_USER_MODEL`, `TEMPLATES`, etc.
- [ ] `BE-04`: Configurar PostgreSQL como motor de base de datos
- [X] `BE-05`: Agregar `landing` y `dashboard` como apps registradas
- [X] `BE-06`: Crear script para carga de fixtures (`user`, `client`, `products`, etc.)

## 2. Autenticación y Roles

- [X] `BE-10`: Extender modelo `User` con campo `role` (`admin`, `client`)
- [X] `BE-11`: Configurar `CustomLoginView` con redirección según rol
- [X] `BE-12`: Vista protegida para panel de admin (`/admin-panel`)
- [X] `BE-13`: Vista protegida para clientes (`/my-orders`)
- [X] `BE-14`: Restricción por rol en views usando validación en `request.user`

## 3. Gestión de Pedidos

- [X] `BE-20`: Modelo `PurchaseOrder` con campos: cliente, total, estado, notas
- [X] `BE-21`: Modelo `OrderItem` relacionado a `PurchaseOrder` y `ProductVariant`
- [X] `BE-22`: Modelo `Product` y `ProductVariant` con atributos personalizables
- [X] `BE-23`: Vista `my_orders.html` que muestra las órdenes del cliente autenticado
- [ ] `BE-24`: Filtrar y agrupar por estado (`pendiente`, `completado`, etc.)
- [ ] `BE-25`: Permitir ver el detalle de cada orden y sus ítems

## 4. Panel Administrativo

- [X] `BE-30`: Crear template base `admin_base.html`
- [X] `BE-31`: Vista `dashboard_home` como inicio del panel admin
- [X] `BE-32`: Crear sidebar reutilizable
- [X] `BE-33`: Vista de clientes registrados (`admin_clients.html`)
- [ ] `BE-34`: Vista de pedidos recibidos agrupados por cliente
- [ ] `BE-35`: Gestión de productos y stock desde el dashboard

## 5. Infraestructura y Extras

- [ ] `BE-40`: Configurar archivos estáticos y media para producción
- [ ] `BE-41`: Implementar `Dockerfile` y `docker-compose.yml` con PostgreSQL
- [ ] `BE-42`: Desplegar en entorno staging o testing (Render, Railway, etc.)
- [X] `BE-43`: Crear estructura `fixtures/` con datos de prueba

---

## Seguimiento General

- Tareas completadas: 19
- Tareas pendientes: 10
- Porcentaje completado: 65.5%
