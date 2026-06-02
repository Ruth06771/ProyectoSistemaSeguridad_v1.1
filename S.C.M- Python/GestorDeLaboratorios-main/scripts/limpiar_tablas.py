import sys
from pathlib import Path

# Add project root to sys.path so `config.db` can be imported when running this script directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.db import get_connection


def get_table_names(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        rows = cursor.fetchall()
        tables = []
        for row in rows:
            if hasattr(row, 'keys'):
                tables.append(row['name'])
            else:
                tables.append(row[0])
        return tables
    finally:
        cursor.close()


def clear_tables(connection, tables):
    cursor = connection.cursor()
    try:
        connection.execute('PRAGMA foreign_keys = OFF;')
        for table in tables:
            cursor.execute(f'DELETE FROM "{table}";')
        cursor.execute('DELETE FROM sqlite_sequence;')
        connection.commit()
    finally:
        cursor.close()


def get_table_counts(connection, tables):
    cursor = connection.cursor()
    try:
        counts = {}
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) AS cnt FROM "{table}"')
            row = cursor.fetchone()
            counts[table] = row[0] if row is not None else 0
        return counts
    finally:
        cursor.close()


if __name__ == '__main__':
    conn = get_connection()
    try:
        tables = get_table_names(conn)
        print('Tablas detectadas:')
        for table in tables:
            print(f' - {table}')

        counts = get_table_counts(conn, tables)
        print('\nConteo antes de la limpieza:')
        for table, count in counts.items():
            print(f' - {table}: {count}')

        clear_tables(conn, tables)

        counts_after = get_table_counts(conn, tables)
        print('\nLimpieza completada. Conteo después de la limpieza:')
        for table, count in counts_after.items():
            print(f' - {table}: {count}')
    finally:
        conn.close()
