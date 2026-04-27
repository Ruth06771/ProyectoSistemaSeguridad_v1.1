import sqlite3
from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
print('DB:', p)
conn = sqlite3.connect(str(p))
conn.row_factory = sqlite3.Row
cur = conn.cursor()
for t in ['movimientos','tarjetas']:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {t}')
        cnt = cur.fetchone()[0]
    except Exception as e:
        print(f"Table {t} error: {e}")
        continue
    print(f"\nTable {t} count: {cnt}")
    try:
        cur.execute(f'SELECT * FROM {t} ORDER BY id DESC LIMIT 10')
        rows = cur.fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print('Read rows error:', e)
cur.close()
conn.close()
