#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
print('DB path:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
try:
    cur.execute('PRAGMA table_info(enrolar)')
    cols = cur.fetchall()
    print('enrolar columns:')
    for c in cols:
        print(' ', c)
    cur.execute('SELECT COUNT(*) FROM enrolar')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM enrolar WHERE tarjeta_id IS NOT NULL')
    with_id = cur.fetchone()[0]
    print('total rows in enrolar:', total)
    print('rows with tarjeta_id not null:', with_id)
except Exception as e:
    print('Error inspecting DB:', e)
finally:
    conn.close()
