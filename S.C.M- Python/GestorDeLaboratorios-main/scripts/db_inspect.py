from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'dev.sqlite3'
if not DB.exists():
    print('No se encontró', DB)
    sys.exit(1)

con = sqlite3.connect(str(DB))
cur = con.cursor()

def sample(table, n=10):
    try:
        cur.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (n,))
        rows = cur.fetchall()
        print(f"\n== {table} (últimas {n} filas) ==")
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error al leer {table}: {e}")

for t in ('personas','tarjetas','historial_tarjetas','historial_accesos'):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        c = cur.fetchone()[0]
        print(f'{t}: {c} filas')
    except Exception as e:
        print(f'{t}: error ->', e)

sample('personas', 5)
sample('tarjetas', 5)
sample('historial_tarjetas', 5)
sample('historial_accesos', 5)
con.close()
