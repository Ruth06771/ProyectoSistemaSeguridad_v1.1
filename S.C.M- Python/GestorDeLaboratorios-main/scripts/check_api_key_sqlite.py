import sqlite3,sys
from pathlib import Path
p=Path('data/dev.sqlite3')
if not p.exists():
    print('dev.sqlite3 not found')
    sys.exit(0)
conn=sqlite3.connect(str(p))
conn.row_factory=sqlite3.Row
cur=conn.cursor()
try:
    cur.execute("SELECT id, nombre, api_key, activo FROM dispositivos WHERE api_key = ?", ('MI_PRUEBA_CLAVE',))
    r=cur.fetchone()
    print('found:', dict(r) if r else None)
except Exception as e:
    print('err:', e)
finally:
    cur.close(); conn.close()
