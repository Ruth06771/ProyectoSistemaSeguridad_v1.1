import sqlite3
from pathlib import Path
p=Path('data/dev.sqlite3')
conn=sqlite3.connect(str(p))
conn.row_factory=sqlite3.Row
cur=conn.cursor()
try:
    # emulate the backend's sqlite logic
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispositivos'")
    if cur.fetchone():
        cur.execute('SELECT id, nombre, api_key, activo, fecha_registro FROM dispositivos')
        rows = cur.fetchall()
        results = [dict(zip(['id','nombre','api_key','activo','fecha_registro'], r)) for r in rows]
    else:
        cur.execute('SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos')
        rows = cur.fetchall()
        results = [dict(zip(['id','nombre','api_key','activo','fecha_registro'], r)) for r in rows]
    print('results count:', len(results))
    for r in results:
        print(r)
finally:
    cur.close(); conn.close()
