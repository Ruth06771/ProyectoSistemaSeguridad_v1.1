import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'data' / 'dev.sqlite3'

ROLES = [
    (1, 'Administradora', 1),
    (2, 'Auxiliar', 1),
    (3, 'Docente', 1),
    (4, 'Estudiante', 1),
]

PERMISOS = [
    (1, 'Configuración', 'Acceso al módulo de configuración'),
    (2, 'Enrolar', 'Acceso al módulo de enrolar'),
    (3, 'Seguridad', 'Acceso al módulo de seguridad'),
    (4, 'Reportes', 'Acceso al módulo de reportes'),
    (5, 'Administración', 'Acceso al módulo de administración (personas, usuarios, dispositivos, etc.)'),
]

ADMIN_ROLE_ID = 1

def connect_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn, table_name):
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,))
        return cur.fetchone() is not None
    finally:
        cur.close()


def insert_roles(conn):
    cur = conn.cursor()
    try:
        for role_id, nombre, estado in ROLES:
            cur.execute(
                "INSERT OR IGNORE INTO rol_sistema (id, nombre, estado) VALUES (?, ?, ?)",
                (role_id, nombre, estado)
            )
        conn.commit()
    finally:
        cur.close()


def insert_permisos(conn):
    cur = conn.cursor()
    try:
        for permiso_id, nombre, descripcion in PERMISOS:
            cur.execute(
                "INSERT OR IGNORE INTO permisos (id, nombre, descripcion) VALUES (?, ?, ?)",
                (permiso_id, nombre, descripcion)
            )
        conn.commit()
    finally:
        cur.close()


def insert_admin_permisos(conn):
    cur = conn.cursor()
    try:
        for permiso_id, _, _ in PERMISOS:
            cur.execute(
                "INSERT OR IGNORE INTO detalle_del_permiso (permiso_id, estado, ver, crear, editar, eliminar, rol_id) VALUES (?, 1, 1, 1, 1, 1, ?)",
                (permiso_id, ADMIN_ROLE_ID)
            )
        conn.commit()
    finally:
        cur.close()


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Base de datos no encontrada: {DB_PATH}")

    conn = connect_db(DB_PATH)
    try:
        required_tables = ['rol_sistema', 'permisos', 'detalle_del_permiso']
        missing = [t for t in required_tables if not table_exists(conn, t)]
        if missing:
            raise RuntimeError(f"Faltan tablas en la base de datos: {', '.join(missing)}")

        insert_roles(conn)
        insert_permisos(conn)
        insert_admin_permisos(conn)

        print('Poblamiento completado con éxito.')
        print('Roles insertados / existentes:')
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, nombre, estado FROM rol_sistema ORDER BY id')
            for row in cur.fetchall():
                print(' ', row['id'], row['nombre'], row['estado'])
            print('\nPermisos insertados / existentes:')
            cur.execute('SELECT id, nombre, descripcion FROM permisos ORDER BY id')
            for row in cur.fetchall():
                print(' ', row['id'], row['nombre'], row['descripcion'])
            print('\nPermisos del rol Administradora:')
            cur.execute('SELECT permiso_id FROM detalle_del_permiso WHERE rol_id = ? ORDER BY permiso_id', (ADMIN_ROLE_ID,))
            for row in cur.fetchall():
                print(' ', row['permiso_id'])
        finally:
            cur.close()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
