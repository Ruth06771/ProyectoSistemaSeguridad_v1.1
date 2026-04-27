"""Small helper to insert a test device into the dev.sqlite3 used by the project.
This version avoids importing the application package to prevent any side-effects
like starting the Flask dev server when run in the project root.

It is idempotent (uses INSERT OR IGNORE) and safe to run locally.
"""
import sqlite3
from pathlib import Path

# Mirror the path logic used by config/db.py to find data/dev.sqlite3
DEV_SQLITE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
DEV_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(DEV_SQLITE_PATH), check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        api_key TEXT NOT NULL UNIQUE,
        activo INTEGER NOT NULL DEFAULT 1,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
    )"""
)

# Ensure api_key column exists (older DBs may have dispositivos without api_key)
try:
    cur.execute("PRAGMA table_info(dispositivos)")
    cols_info = cur.fetchall()
    cols = [c['name'] if isinstance(c, sqlite3.Row) else c[1] for c in cols_info]
except Exception:
    cols = []

if 'api_key' not in cols:
    # Add column; SQLite's ALTER TABLE supports adding a column with a default
    try:
        cur.execute("ALTER TABLE dispositivos ADD COLUMN api_key TEXT")
        conn.commit()
        print('Added missing column api_key to dispositivos')
    except Exception as e:
        print('Could not add api_key column:', e)

# Determine column names to use for insert (support PascalCase legacy schema)
try:
    cur.execute("PRAGMA table_info(dispositivos)")
    cols_info = cur.fetchall()
    cols = [c['name'] if isinstance(c, sqlite3.Row) else c[1] for c in cols_info]
except Exception:
    cols = []

name_col = 'nombre' if 'nombre' in cols else ('Nombre' if 'Nombre' in cols else None)
api_col = 'api_key' if 'api_key' in cols else ('ApiKey' if 'ApiKey' in cols else None)
activo_col = 'activo' if 'activo' in cols else ('Activo' if 'Activo' in cols else None)

try:
    # Add missing snake_case helper columns to keep dev environment consistent
    if 'nombre' not in cols:
        cur.execute("ALTER TABLE dispositivos ADD COLUMN nombre TEXT")
        conn.commit()
        cols.append('nombre')
        name_col = 'nombre'
        print('Added missing column nombre to dispositivos')
    if 'activo' not in cols:
        cur.execute("ALTER TABLE dispositivos ADD COLUMN activo INTEGER DEFAULT 1")
        conn.commit()
        cols.append('activo')
        activo_col = 'activo'
        print('Added missing column activo to dispositivos')
    if 'api_key' not in cols and 'ApiKey' in cols:
        # keep api_col as ApiKey if only that exists
        api_col = 'ApiKey'
    elif 'api_key' not in cols and 'ApiKey' not in cols:
        # if neither exists, add api_key
        cur.execute("ALTER TABLE dispositivos ADD COLUMN api_key TEXT")
        conn.commit()
        cols.append('api_key')
        api_col = 'api_key'
        print('Added missing column api_key to dispositivos')
except Exception as e:
    print('Could not add missing columns:', e)

# Build insert using whichever column names exist (prefer snake_case)
insert_cols = []
insert_vals = []
if name_col:
    insert_cols.append(name_col)
    insert_vals.append('ESP32-Test')
if api_col:
    insert_cols.append(api_col)
    insert_vals.append('MI_PRUEBA_CLAVE')
if activo_col:
    insert_cols.append(activo_col)
    insert_vals.append(1)

if insert_cols:
    placeholders = ','.join(['?'] * len(insert_cols))
    sql = f"INSERT OR IGNORE INTO dispositivos ({','.join(insert_cols)}) VALUES ({placeholders})"
    try:
        cur.execute(sql, tuple(insert_vals))
        conn.commit()
    except Exception as e:
        print('Insert failed:', e)
else:
    print('No suitable columns found to insert a dispositivo row')

# Select a set of columns that exist for display
select_cols = []
for candidate in ['id', 'IdDispositivo', 'nombre', 'Nombre', 'api_key', 'ApiKey', 'activo', 'Activo', 'fecha_registro', 'FechaRegistro']:
    if candidate in cols and candidate not in select_cols:
        select_cols.append(candidate)

if not select_cols:
    # fallback to select * if we couldn't determine columns
    select_sql = 'SELECT * FROM dispositivos'
else:
    select_sql = 'SELECT ' + ','.join(select_cols) + ' FROM dispositivos'

try:
    cur.execute(select_sql)
    rows = cur.fetchall()
    print('Dispositivos in DB:')
    for r in rows:
        try:
            print(dict(r))
        except Exception:
            print(r)
except Exception as e:
    print('Select failed:', e)

cur.close()
conn.close()
