# CHANGELOG

## 2025-09-30 — Fixes y mejoras aplicadas

- Frontend
  - `frontend/src/modulos/administracion/personas/Personas.jsx`: Añadido botón y lógica para eliminar personas (DELETE `/api/personas/:id`).
  - `frontend/src/modulos/accesos/NuevaTarjetaRFID.jsx` (y copia en `modulos/`): Corregido endpoint POST a `/api/tarjetas` y añadido `credentials: 'include'`. Mejora de manejo de errores.
  - `frontend/src/dashboard/AdminDashboard.jsx`: Añadidos fetches para reportes y wiring de resultados/filtros hacia componentes de reportes.
  - `frontend/dist/` (build) con Vite para incluir cambios.

- Backend
  - `modulos/reportes/reportes_api.py`: Actualizadas consultas SQL para usar `historial_accesos` y `historial_tarjetas` (tablas del SQLite de desarrollo).
  - `modulos/administracion/personas/personas_api.py`: Confirmada existencia de DELETE `/api/personas/<id>` y normalización de placeholders para sqlite/mysql.
  - `modulos/accesos/tarjetas_api.py`: Confirmada API POST/GET/PUT/DELETE para tarjetas.

- Infra / utilidades
  - `scripts/db_inspect.py`: Script para imprimir conteos y muestras de tablas en `data/dev.sqlite3`.
  - `scripts/list_routes.py`: Script para listar las rutas registradas por Flask.
  - `APIS.md`: Documentación resumida de endpoints.
  - `README.md`: Actualizada sección "Cómo ver los registros..." y añadido changelog corto.

Notas
- Se insertaron filas de prueba en `data/dev.sqlite3` durante debugging para validar endpoints de reportes.
- Inserté filas de prueba en `data/dev.sqlite3` durante debugging para validar endpoints de reportes.
