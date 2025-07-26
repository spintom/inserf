# 04. Infraestructura y Extras - INSERF

Este documento describe los elementos adicionales que componen la infraestructura del proyecto INSERF, incluyendo soporte para entorno de desarrollo, carga de datos y documentación técnica.

---

## Docker y Entorno de Desarrollo

- Configuración del entorno local basada en SQLite para simplicidad inicial.
- Pendiente implementación de `Dockerfile` y `docker-compose.yml` para contenerización y despliegue futuro.
- Se recomienda agregar soporte a PostgreSQL como base de datos de producción.

---

## Fixtures de Datos

La carpeta `dashboard/fixtures/` contiene archivos `.json` para precargar información clave en el sistema:

- `user.json`: Crea un usuario admin (`admin`) y un usuario cliente (`cliente`).
- `clients.json`: Define clientes asociados al rol cliente.
- `products.json`: Define productos base para pruebas.
- `product_variants.json`: Variantes de producto con stock inicial.
- `purchase_orders.json`: Pedidos realizados por clientes.
- `order_items.json`: Ítems asociados a cada pedido.

Estos datos pueden cargarse con:

```

python manage.py loaddata dashboard/fixtures/\*.json

```

---

## Estructura de Rutas

Se han definido rutas limpias y segmentadas:

- `/`: Landing page pública
- `/login/`: Autenticación
- `/my-orders/`: Vista protegida para clientes
- `/admin-panel/`: Vista protegida para administradores

---

## Estilos y Recursos Estáticos

- Archivos CSS y multimedia se encuentran en `landing/static/`.
- Imágenes optimizadas y organizadas por función (logos, banners, etc).
- Bootstrap 5 y AOS se cargan desde CDN.

---

## Documentación y Organización

Se mantiene una estructura de documentación interna en archivos `.md`, incluyendo:

- Checklist de tareas (`12-tree-tasks.md`)
- Modelo de entidades (`11-model-entities.md`)
- Estructura del proyecto (`10-project-structure.md`)
- Archivos futuros para despliegue y testing automatizado

---

## Siguientes Pasos

- Agregar soporte para PostgreSQL como base de datos final.
- Definir `Dockerfile` y `docker-compose.yml` para facilitar desarrollo colaborativo y pruebas.
- Configurar entorno staging o testing para pruebas con datos reales.