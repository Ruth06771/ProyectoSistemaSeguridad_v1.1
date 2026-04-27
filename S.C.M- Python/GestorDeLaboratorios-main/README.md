# GestorDeLaboratorios — README

Última actualización: 30-09-2025

Este documento resume las dependencias del proyecto, los cambios que se realizaron durante la migración y refactorización, cómo ejecutar el sistema en desarrollo (incluido el fallback a SQLite), y una presentación corta tipo "Shark Tank" para exponer el producto ante inversores.

## Resumen del proyecto

GestorDeLaboratorios es una aplicación web para gestionar personas, accesos y reportes en un entorno académico/administrativo. Tiene un backend en Python/Flask que expone APIs REST y un frontend moderno en React con Vite.

## Principales decisiones técnicas (resumen)
- Backend: Flask (Python). APIs organizadas por blueprints en `modulos/*`.
- Frontend: React (Vite) en `frontend/` (migración de vistas HTML a React está en curso/implementada parcialmente).
- Base de datos: Soporta MySQL (producción) y un fallback automático a SQLite para desarrollo local (`data/dev.sqlite3`).
- Exportes: Reportes en PDF (ReportLab) y Excel (openpyxl) en el backend.

## Dependencias

Backend (Python)
- Requiere Python 3.11+ (probado con Python 3.13 en este entorno).
- Paquetes pip (instalar dentro de un virtualenv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors pymysql reportlab openpyxl
```

- Nota: `sqlite3` viene incluido con Python y se usa como fallback de desarrollo.

Frontend (Node.js)
- Node.js + npm (recomendado: Node 18+)
- Desde la carpeta `frontend/`:

```powershell
cd frontend
npm install
npm run dev
```

Dependencias clave del frontend (ya listadas en `frontend/package.json`): React, Vite, Bootstrap.

## Configuración de base de datos
- Para usar MySQL (producción), exporta las variables de entorno antes de lanzar el backend:

```powershell
$env:DB_HOST = 'tu_host'
$env:DB_USER = 'tu_usuario'
$env:DB_PASSWORD = 'tu_password'
$env:DB_NAME = 'tu_basedatos'
```

- Si no están presentes (o la conexión falla), el backend usa automáticamente `data/dev.sqlite3` y crea un esquema mínimo (tabla `personas`) para desarrollo y pruebas locales.

## Cómo ejecutar (desarrollo, PowerShell)

1) Preparar entorno Python

```powershell
cd "C:\Users\Usuario\OneDrive\Imágenes\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # si no existe, instalar: flask flask-cors pymysql reportlab openpyxl
```

2) Levantar backend (Flask)

```powershell
# desde la carpeta del backend
python auth\login_api.py
```

3) Levantar frontend (opcional, en otra terminal)

```powershell
cd frontend
npm install
npm run dev
```

4) Pruebas rápidas que ejecuté aquí
- `tmp_create_persona_verbose.py`: realiza un POST a `http://127.0.0.1:5000/api/personas`. Resultado esperado: HTTP 200 y `{"success": true}` si la inserción fue correcta. Si MySQL no está activo, se usa SQLite local.

## Cambios y refactorizaciones realizados (listado y propósito)

He realizado una serie de cambios para consolidar la configuración de BD, compatibilizar el backend con MySQL y SQLite, migrar parcialmente vistas a React y mejorar la robustez del código. Aquí el resumen por áreas y archivos modificados:

- `config/db.py`
  - Centraliza la conexión a BD. Intenta MySQL (por variables de entorno) y si falla crea/usa `data/dev.sqlite3`. Añade schema mínimo para `personas`.

- `auth/login_api.py`
  - Se aseguró que el directorio raíz esté en `sys.path` para cargar blueprints correctamente; registra módulos API.

- `modulos/administracion/personas/personas_api.py`
  - Añadido `try_get_connection()` y refactor para usar cursor manual, adaptación de placeholders (`%s` → `?` en SQLite), normalización de filas y manejo de errores JSON claros.

- `modulos/administracion/personas/editar.py`
  - Reemplazado `with connection.cursor() as cursor:` por patrón compatible con ambos motores; carga de plantilla HTML si existe (`editar.html`), validaciones y commits seguros.

- `modulos/accesos/index.py` y `modulos/accesos/tarjetas_api.py`
  - Adaptadas consultas/updates para funcionar con SQLite y MySQL, normalización de resultados y cierre seguro de cursores.

- `modulos/reportes/*`
  - Varias funciones de export (PDF/Excel) adaptadas a la normalización de cursores y a la conversión de placeholders. Aún queda validar formatos con el esquema final de producción.

- Frontend (React)
  - Componentes `frontend/src/modulos/ModuloReportesTabla.jsx` y `frontend/src/modulos/reportes/ReporteTarjetasPDF.jsx` vieron añadidos botones de navegación "← Volver al Módulo de Reportes" y reubicación de los ficheros en `frontend/` si aún no estaban.

- Scripts temporales de pruebas
  - `tmp_create_persona_verbose.py`, `tmp_check_personas.py`, `tmp_list_routes.py` — herramientas usadas para verificar imports, rutas y la conexión DB.

Si quieres, puedo añadir un CHANGELOG.md con diffs por commit o preparar un PR que muestre cada cambio en detalle.

## Casos borde y notas técnicas
- Placeholders SQL: pymysql usa `%s`, sqlite3 usa `?`. El backend detecta el driver y adapta los queries automáticamente.
- Cursor context manager: `with connection.cursor() as cursor` no es compatible con sqlite3, por eso se sustituyó por un patrón manual y cierres en finally.
- Concurrencia: El servidor Flask de desarrollo no es para producción. Para producción usar Gunicorn / uWSGI + Nginx y un pool de conexiones para MySQL.

## Quick smoke tests (lo que ejecuté aquí)
- Inicié el backend: `python auth\login_api.py`.
- Ejecuté `tmp_create_persona_verbose.py` desde la raíz del backend; respuesta: `Status: 200` y `{"success": true}`. Esto confirma que la API está vinculada y funciona con el fallback SQLite si MySQL no está disponible.

## Cómo ver los registros que hace la base de datos (consultas y filas)

Aquí tienes varias formas prácticas de inspeccionar los datos y la actividad de la base de datos local (`data/dev.sqlite3`) y de ver los logs de la aplicación.

1) Usar la utilidad sqlite3 (desde PowerShell)

```powershell
# Abrir una sesión interactiva con la base de datos sqlite
cd "C:\Users\Usuario\OneDrive\Imágenes\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main"
sqlite3.exe data\dev.sqlite3

-- En el prompt de sqlite3 puedes ejecutar:
-- Listar tablas
.tables
-- Ver esquema de una tabla (ej. historial_tarjetas)
.schema historial_tarjetas
-- Ver las últimas 50 filas de personas
SELECT * FROM personas ORDER BY id DESC LIMIT 50;
-- Contar filas de tablas clave
SELECT 'personas' as tabla, COUNT(*) as filas FROM personas;
SELECT 'tarjetas' as tabla, COUNT(*) as filas FROM tarjetas;
SELECT 'historial_tarjetas' as tabla, COUNT(*) as filas FROM historial_tarjetas;
```

Si no tienes `sqlite3.exe` en Windows puedes instalar el paquete oficial desde sqlite.org o usar `DB Browser for SQLite` (GUI).

2) Usar un script Python rápido (recomendado y portable)

Guarda este snippet como `scripts/db_inspect.py` (opcional) y ejecútalo desde la raíz del proyecto con tu entorno virtual activado:

```python
"""Imprime conteos y muestras de tablas clave en data/dev.sqlite3"""
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / 'data' / 'dev.sqlite3'
print('DB:', db)
if not db.exists():
    raise SystemExit('No se encontró data/dev.sqlite3')

con = sqlite3.connect(str(db))
cur = con.cursor()
def sample(table, n=10):
    cur.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    print(f'\n== {table} (últimas {n} filas) ==')
    for r in rows:
        print(r)

for t in ('personas','tarjetas','historial_tarjetas','historial_accesos'):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        c = cur.fetchone()[0]
        print(f'{t}: {c} filas')
    except Exception as e:
        print(f'{t}: error ->', e)

sample('personas', 5)
sample('tarjetas', 5)
sample('historial_tarjetas', 5)
sample('historial_accesos', 5)
con.close()
```

Ejecución (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
python scripts\db_inspect.py
```

3) Ver logs de la aplicación (Flask) en tiempo real

Durante desarrollo Flask imprime logs por consola. Si ejecutas la app en una terminal verás las peticiones y errores. También este repositorio contiene `flask_out.log` y `flask_err.log` (si el servidor fue redirigido a archivos). Para seguirlos en PowerShell:

```powershell
# Ver últimos 200 líneas y mantener la vista en tiempo real
Get-Content -Path .\flask_out.log -Wait -Tail 200
Get-Content -Path .\flask_err.log -Wait -Tail 200
```

Si no tienes esos archivos, ejecuta el servidor en una terminal para ver logs en directo:

```powershell
cd "C:\Users\Usuario\OneDrive\Imágenes\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main"
python auth\login_api.py
```

4) Si usas MySQL (producción)

Conéctate con el cliente `mysql` y ejecuta consultas estándar:

```powershell
mysql -h $env:DB_HOST -u $env:DB_USER -p $env:DB_NAME
-- En SQL:
SHOW TABLES;
SELECT COUNT(*) FROM personas;
SELECT * FROM historial_tarjetas ORDER BY id DESC LIMIT 20;
```

5) Depuración de errores de red en el navegador

Si al registrar tarjetas ves "Error de red":
- Asegúrate de que el backend está corriendo (`python auth\login_api.py`) antes de usar la UI.
- Abre DevTools → Pestaña Network y reproduce la acción. Copia el estado HTTP (200/401/500/0), el response body y cualquier error de consola. Esto es lo que yo necesitaré para diagnosticar el problema desde el lado cliente.

## Changelog

Lista compacta de archivos modificados y por qué (fixes aplicados):

- `frontend/src/modulos/administracion/personas/Personas.jsx`
  - Añadí el botón y la lógica para eliminar personas desde la UI (DELETE `/api/personas/:id`), refresco de la lista y mensajes de estado.
- `frontend/src/modulos/accesos/NuevaTarjetaRFID.jsx` (y copia en `modulos/`)
  - Corregí el endpoint POST a `/api/tarjetas` (antes usaba `/api/tarjeta`) y añadí `credentials: 'include'` y mejor manejo de errores para que el cliente vea mensajes claros.
- `frontend/src/dashboard/AdminDashboard.jsx`
  - Añadidas funciones para cargar los reportes (fetch a `/api/reportes/*`) y pasé resultados y filtros a los componentes de reportes; añadí hooks para refrescar cuando se selecciona un reporte.
- `modulos/reportes/reportes_api.py`
  - Actualicé las consultas SQL para usar las tablas reales presentes en `data/dev.sqlite3` (`historial_accesos` y `historial_tarjetas`) y normalicé el manejo de cursores.
- `config/db.py`
  - (No modificado en esta sesión, listado aquí porque lo uso para explicar cómo detectar qué motor está activo). Mantiene fallback a `data/dev.sqlite3`.
- `data/dev.sqlite3`
  - Inserción puntual de filas de prueba en `historial_accesos` y `historial_tarjetas` para verificar que los endpoints de reportes devuelven datos durante el debug.
-- `frontend/dist/` (build)
  - Build del frontend (Vite) para que las correcciones de frontend se reflejen en los assets usados por el navegador.

Notas rápidas:
- Si ves datos en los endpoints (GET `/api/reportes/*`) desde una terminal o `curl` pero no en la UI, revisa que el servidor estuviera levantado en el momento en que abriste la web y que no estés cargando versiones antiguas de `dist/` en cache (Ctrl+F5 para forzar reload).
- Para operaciones con sesión (login) las peticiones del frontend usan `credentials: 'include'`; el servidor debe estar en la misma ruta/host o configurar CORS/credentials correctamente.

## Próximos pasos recomendados
1. Proporcionar credenciales MySQL (o levantar el servicio) para probar consultas y exportes contra el esquema real.
2. Completar la migración de todas las vistas HTML restantes a React y eliminar las plantillas server-side cuando la UI esté completa.
3. Añadir tests automatizados (pytest) para endpoints clave: login, CRUD personas, exportes.
4. Preparar despliegue: Dockerfile para backend y frontend, y pipeline CI que ejecute tests y cree imágenes.

## Documentación y ubicación de archivos importantes
La documentación se encuentra en la carpeta `docs/`. Dentro de `docs/` encontrarás:

- `APIS.md` — resumen de endpoints y rutas importantes.
- `CHANGELOG.md` — resumen de cambios aplicados por fecha.
- `README-backend.md` — instrucciones específicas para trabajar con el backend.
- `README-frontend.md` — instrucciones específicas para trabajar con el frontend.

Si prefieres que mueva físicamente las carpetas del código (opción B), puedo hacerlo y actualizar imports; te lo agradezco si confirmas.

## Presentación tipo "Shark Tank" (versión corta, lista para pitch)

Problema: Las universidades y centros de investigación gestionan manualmente accesos, fichas personales y reportes, lo que provoca pérdida de tiempo, errores y fricción administrativa.

Solución: GestorDeLaboratorios es una plataforma ligera, modular y lista para integrarse en infraestructuras institucionales. Permite:

- Registrar y editar personas con validaciones.
- Gestionar tarjetas de acceso y su historial.
- Generar reportes y exportarlos en PDF/Excel desde el backend (ideal para auditorías).

Ventaja competitiva:
- Integración lista con MySQL (producción) y fallback automático a SQLite para desarrollo — despliegue y pruebas sin fricciones.
- API-first: cualquier frontend (React, móvil o sistemas externos) puede consumir las APIs.
- Componentes modulares que facilitan añadir nuevos módulos (equipos, inventario, reservaciones).

Tracción mínima viable y uso propuesto:
- Equipo técnico puede desplegar una instancia en horas y comenzar a reemplazar hojas de cálculo y procesos manuales.
- Ideal para laboratorios universitarios, administración de campus y centros de I+D.

La petición (qué buscamos): inversión o colaboración técnica para:

- Integrar autenticación SSO (LDAP / OAuth2) y endurecer seguridad (HTTPS, WAF).
- Preparar un despliegue productivo en la nube o en la red institucional (Docker + Kubernetes opcional).

En una frase para los sharks: "Somos la capa ligera y modular que transforma procesos administrativos manuales en flujos digitales seguros y auditables para universidades y centros de investigación — listo para pilotar en 30 días." 

---

Si quieres, agrego:
- Un `requirements.txt` y un `package.json` mínimo si faltan.
- Un CHANGELOG con cada archivo modificado y el diff aplicado.
- Tests automatizados (pytest) para los endpoints esenciales.

Dime qué prefieres que haga a continuación y lo implemento: pruebas E2E automáticas, conectar tu MySQL real (con instrucciones para poner credenciales seguras), o preparar artefactos para despliegue (Dockerfiles, CI).
