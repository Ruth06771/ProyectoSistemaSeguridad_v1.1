import sqlite3
import os

path = os.path.abspath(os.path.join('data', 'dev.sqlite3'))
print('DB:', path, os.path.exists(path))
conn = sqlite3.connect(path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
uid = 'E3314E1C'
print('\nTARJETA:')
cur.execute('SELECT id, uid, pin, estado FROM tarjetas WHERE uid = ?', (uid,))
for row in cur.fetchall():
    print(dict(row))
print('\nENROLAR matches:')
cur.execute('SELECT id, tarjeta_uid, tarjeta_id, estado FROM enrolar WHERE tarjeta_uid = ? OR tarjeta_id = ? LIMIT 100', (uid, 22))
rows = cur.fetchall()
print(len(rows))
for row in rows:
    print(dict(row))
print('\nTOTAL ENROLAR:')
cur.execute('SELECT id, tarjeta_uid, tarjeta_id, estado FROM enrolar ORDER BY id')
rows = cur.fetchall()
print(len(rows))
for row in rows:
    print(dict(row))
conn.close()
