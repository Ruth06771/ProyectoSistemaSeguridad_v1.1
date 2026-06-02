"""Script para limpiar historial de accesos (registro_acceso y historial_accesos).
Usa la función get_connection() de config.db para conectarse a la BD del proyecto.
Imprime conteos antes y después y hace VACUUM si es sqlite.
"""
import traceback
import os
import sys

# Make project root importable when running this script directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.db import get_connection


def main():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            inspect_tables = ['registro_acceso', 'historial_accesos', 'historial_tarjetas', 'historial_enrolamiento']
            counts_before = {}
            for t in inspect_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) as c FROM {t}")
                    r = cur.fetchone()
                    counts_before[t] = r[0] if r else 0
                except Exception:
                    counts_before[t] = None

            print('Conteos antes:')
            for t, c in counts_before.items():
                print(f' - {t}: {c}')

            # Delete only control de accesos
            try:
                cur.execute('DELETE FROM registro_acceso')
                conn.commit()
                print('Deleted rows from registro_acceso')
            except Exception as e:
                print(f'Could not clear registro_acceso: {e}')

            counts_after = {}
            for t in inspect_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) as c FROM {t}")
                    r = cur.fetchone()
                    counts_after[t] = r[0] if r else 0
                except Exception:
                    counts_after[t] = None

            print('\nConteos después:')
            for t, c in counts_after.items():
                print(f' - {t}: {c}')

            # If sqlite, vacuum
            if conn.__class__.__module__.startswith('sqlite3'):
                try:
                    cur.execute('VACUUM')
                    print('\nVACUUM ejecutado')
                except Exception:
                    pass
        finally:
            try:
                cur.close()
            except Exception:
                pass
    except Exception:
        traceback.print_exc()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
