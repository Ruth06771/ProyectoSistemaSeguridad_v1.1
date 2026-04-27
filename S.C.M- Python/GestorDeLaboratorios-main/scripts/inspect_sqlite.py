import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
print('db:', db)
conn = sqlite3.connect(str(db))
cur = conn.cursor()
print('tables:', [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
for t in ['historial_tarjetas','historial_accesos','historial_acciones','registro_acceso','personas','tarjetas']:
    try:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()]
        print(t, cols)
    except Exception as e:
        print(t, 'ERR', e)
conn.close()
