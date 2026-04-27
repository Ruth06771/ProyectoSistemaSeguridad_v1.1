import sqlite3
from pathlib import Path
p=Path('data/dev.sqlite3')
conn=sqlite3.connect(str(p))
cur=conn.cursor()
cur.execute("SELECT type,name,sql FROM sqlite_master WHERE name LIKE '%Dispositivos%' OR name LIKE 'dispositivos'")
for r in cur.fetchall():
    print(r)
cur.close(); conn.close()
