#!/usr/bin/env python3
"""
Comprueba la migración de la tabla `enrolar` y muestra columnas y resumen de `tarjeta_id`.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.db import get_connection


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(enrolar)")
        cols = cur.fetchall()
        print('enrolar columns:')
        for c in cols:
            # c is sqlite3.Row
            print(f"  {c['name']} (type={c['type']})")
        cur.execute('SELECT COUNT(*) FROM enrolar')
        total = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM enrolar WHERE tarjeta_id IS NOT NULL')
        with_id = cur.fetchone()[0]
        print(f"total rows in enrolar: {total}")
        print(f"rows with tarjeta_id not null: {with_id}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
