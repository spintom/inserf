# 05. Revisión Manual - INSERF

Este módulo está planificado para permitir la inspección y corrección de decisiones automatizadas por parte de un analista humano, una vez que se implemente la capa de scoring y evaluación de reglas.

---

## Objetivo

Permitir que un analista revise manualmente los eventos marcados como sospechosos, pueda editar decisiones previamente generadas por el sistema, y auditar esas decisiones con trazabilidad completa.

---

## Funcionalidades Esperadas

- Listar eventos con decisión automática (`accept`, `reject`, `review`)
- Filtrar eventos por fecha, score, reglas activadas, etc.
- Permitir modificar una decisión de forma manual con justificación
- Registrar en auditoría toda modificación manual

---

## Endpoints Planeados

- `GET /dashboard`: Mostrar eventos con estado y score
- `PUT /decisions/:id`: Actualizar decisión con un nuevo estado y razón
- `GET /decisions/:id`: Ver detalle de la decisión con historial de cambios

---

## Reglas de Seguridad

- Sólo usuarios con rol `analyst` podrán acceder a este panel
- Se deberá implementar un `WebFilter` para proteger las rutas
- Toda modificación manual debe quedar registrada en `AuditLog`

---

## Estados de Decisión

- `accepted`: Aprobada automáticamente o por analista
- `rejected`: Rechazada automáticamente o por analista
- `review`: En espera de revisión manual
- `manual_override`: Modificada por el analista respecto a la decisión automática

---

## Campos requeridos para la modificación

- `status`: Nuevo estado de la decisión
- `reason`: Justificación manual
- `author`: Usuario que modificó
- `timestamp`: Fecha de modificación

---

## Observaciones

- Este módulo requiere que previamente esté disponible el flujo completo de eventos, scoring, reglas y decisiones.
- La interfaz se podrá construir en una vista tipo tabla (HTML o frontend externo) con filtros por columna y botones para editar decisión.