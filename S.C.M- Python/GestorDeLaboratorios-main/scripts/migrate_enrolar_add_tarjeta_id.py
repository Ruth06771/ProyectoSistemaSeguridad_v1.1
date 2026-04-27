#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
print('DB path:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info(enrolar)")
    cols = [r[1] for r in cur.fetchall()]
    print('existing columns:', cols)
    if 'tarjeta_id' not in cols:
        print('Adding tarjeta_id column...')
        cur.execute('ALTER TABLE enrolar ADD COLUMN tarjeta_id INTEGER')
        conn.commit()
        print('Populating tarjeta_id from tarjeta_uid if present...')
        if 'tarjeta_uid' in cols:
            try:
                cur.execute('''
                    UPDATE enrolar
                    SET tarjeta_id = (
                        SELECT id FROM tarjetas WHERE tarjetas.uid = enrolar.tarjeta_uid
                    )
                    WHERE tarjeta_uid IS NOT NULL
                ''')
                conn.commit()
            except Exception as e:
                print('Population failed:', e)
    else:
        print('tarjeta_id already exists; nothing to do')
except Exception as e:
    print('Migration error:', e)
finally:
    conn.close()
    print('Done')
