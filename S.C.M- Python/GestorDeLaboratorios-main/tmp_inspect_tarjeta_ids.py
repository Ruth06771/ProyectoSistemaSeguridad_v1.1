import sqlite3

conn = sqlite3.connect('data/dev.sqlite3')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
for tid in [21, 22]:
    cur.execute('SELECT id, uid, pin, estado FROM tarjetas WHERE id = ?', (tid,))
    rows = cur.fetchall()
    print('TARJETA', tid, len(rows))
    for r in rows:
        print(dict(r))
conn.close()
