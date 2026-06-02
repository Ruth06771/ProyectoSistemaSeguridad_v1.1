"""Restaura tablas de historial desde data/dev.sqlite3.bak a data/dev.sqlite3.
Copia `historial_tarjetas` y `historial_enrolamiento` del backup al DB activo usando ATTACH.
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'dev.sqlite3')
BACKUP_PATH = os.path.join(BASE_DIR, 'data', 'dev.sqlite3.bak')

TABLES = ['historial_tarjetas', 'historial_enrolamiento']


def main():
    if not os.path.exists(DB_PATH):
        print('DB active not found:', DB_PATH)
        return
    if not os.path.exists(BACKUP_PATH):
        print('Backup DB not found:', BACKUP_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        try:
            cur.execute(f"ATTACH DATABASE '{BACKUP_PATH}' AS src")
            for t in TABLES:
                try:
                    # Count rows in backup
                    cur.execute(f"SELECT COUNT(*) FROM src.{t}")
                    src_count = cur.fetchone()[0]
                except Exception as e:
                    print(f"Tabla {t} no existe en backup: {e}")
                    src_count = 0
                if src_count <= 0:
                    print(f"No hay filas para {t} en backup, omitiendo")
                    continue

                # Copy rows from src to main; use INSERT OR IGNORE to avoid duplicates
                try:
                    cur.execute('BEGIN')
                    cur.execute(f"INSERT OR IGNORE INTO {t} SELECT * FROM src.{t}")
                    cur.execute('COMMIT')
                    cur.execute(f"SELECT COUNT(*) FROM {t}")
                    new_count = cur.fetchone()[0]
                    print(f"Restaurada tabla {t}: total ahora {new_count}")
                except Exception as e:
                    print(f"Error copiando tabla {t}: {e}")
                    cur.execute('ROLLBACK')
            cur.execute("DETACH DATABASE src")
        finally:
            try:
                cur.close()
            except Exception:
                pass
    finally:
        conn.close()

if __name__ == '__main__':
    main()
