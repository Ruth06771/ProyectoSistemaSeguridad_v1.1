"""Create a SQLite view `dispositivos` that maps PascalCase `Dispositivos` columns to snake_case names.
This is non-destructive and allows runtime code to query `dispositivos` as if it were a snake_case table.
"""
import sqlite3
from pathlib import Path
p = Path('data/dev.sqlite3')
if not p.exists():
    print('dev.sqlite3 not found')
    raise SystemExit(1)
conn = sqlite3.connect(str(p))
cur = conn.cursor()
# Check if PascalCase table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Dispositivos'")
if cur.fetchone():
    # Create or replace view dispositivos
    try:
        cur.execute("DROP VIEW IF EXISTS dispositivos")
        cur.execute("CREATE VIEW dispositivos AS SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos")
        conn.commit()
        print('Created view dispositivos mapping from Dispositivos')
    except Exception as e:
        print('Error creating view:', e)
else:
    print('No PascalCase Dispositivos table found; nothing to do')
cur.close(); conn.close()
