import sqlite3
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(ROOT, 'data', 'dev.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute('SELECT IdDispositivo,Nombre,ApiKey,Activo FROM Dispositivos')
    rows = cur.fetchall()
    print(rows)
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
