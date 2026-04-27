README del backend

Este README contiene instrucciones específicas para trabajar con la parte backend (Flask, módulos, DB)

Arranque rápido
- Activar entorno virtual (opcional):
  .\.venv\Scripts\Activate.ps1
- Ejecutar servidor:
  python auth\login_api.py

Scripts útiles en `scripts/`:
- db_inspect.py: imprime conteos y muestras de tablas en data/dev.sqlite3
- list_routes.py: lista las rutas registradas por Flask

Base de datos
- Fallback a sqlite: data/dev.sqlite3
- Para producción configurar variables de entorno DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

Logs
- flask_out.log, flask_err.log (si existen) o logs en consola cuando se ejecuta el servidor
