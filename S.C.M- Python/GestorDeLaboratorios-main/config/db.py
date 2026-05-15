import os
import sqlite3
from pathlib import Path

# Configurable list of allowed email domains (coma-separados en la variable de entorno)
EMAIL_ALLOWED_DOMAINS = [d.strip().lower() for d in os.environ.get('EMAIL_ALLOWED_DOMAINS', 'ueb.edu.bo').split(',') if d.strip()]

# ============================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================

DEV_SQLITE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'dev.sqlite3'
DEV_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Devuelve una conexión sqlite3 con row_factory configurada y asegura el esquema."""
    conn = sqlite3.connect(str(DEV_SQLITE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _ensure_sqlite_schema(conn)
    return conn


def _ensure_sqlite_schema(conn):
    """Crea las tablas necesarias si no existen. Usa nombres en snake_case coherentes con el resto del código."""
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    # tablas maestras / auxiliares
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tipo_sangre (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        estado INTEGER DEFAULT 1
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS persona_emergencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombres TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        telefono_personal TEXT,
        estado INTEGER DEFAULT 1
    )
    ''')

    # personas
    cur.execute('''
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        fecha_nacimiento TEXT,
        correo TEXT,
        telefono_personal TEXT,
        documento_identidad TEXT,
        sexo TEXT,
        tipo_sangre INTEGER,
        rol TEXT,
        estado INTEGER DEFAULT 1, 
        persona_emergencia INTEGER,
        telefono_emergencia TEXT,
        FOREIGN KEY(tipo_sangre) REFERENCES tipo_sangre(id),
        FOREIGN KEY(persona_emergencia) REFERENCES persona_emergencia(id)
    )
    ''')

    # roles y usuarios
    cur.execute('''
    CREATE TABLE IF NOT EXISTS rol_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        estado INTEGER DEFAULT 1
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuario_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER,
        nombre_usuario TEXT UNIQUE,
        contrasena TEXT,
        rol_id INTEGER,
        estado INTEGER DEFAULT 1,
        FOREIGN KEY(persona_id) REFERENCES personas(id),
        FOREIGN KEY(rol_id) REFERENCES rol_sistema(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS permisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        estado INTEGER DEFAULT 1
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS detalle_del_permiso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permiso_id INTEGER,
        estado INTEGER DEFAULT 1,
        rol_id INTEGER,
        FOREIGN KEY(permiso_id) REFERENCES permisos(id),
        FOREIGN KEY(rol_id) REFERENCES rol_sistema(id)
    )
    ''')

    # perfil acceso
    cur.execute('''
    CREATE TABLE IF NOT EXISTS perfil_acceso_lab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        estado INTEGER DEFAULT 1
    )
    ''')

    # tarjetas
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tarjetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE NOT NULL,
        pin TEXT,
        estado INTEGER DEFAULT 1,
        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # If the 'pin' column was added later, ensure existing DB has the column
    try:
        cur.execute("PRAGMA table_info(tarjetas)")
        cols = [r['name'] for r in cur.fetchall()]
        if 'pin' not in cols:
            try:
                cur.execute('ALTER TABLE tarjetas ADD COLUMN pin TEXT')
            except Exception:
                # Some SQLite versions or backends may not allow ALTER; ignore if it fails
                pass
    except Exception:
        pass

    # Ensure personas table has 'estado' column (for existing DBs)
    try:
        cur.execute("PRAGMA table_info(personas)")
        cols = [r['name'] for r in cur.fetchall()]
        if 'estado' not in cols:
            try:
                cur.execute('ALTER TABLE personas ADD COLUMN estado INTEGER DEFAULT 1')
            except Exception:
                # ignore if ALTER fails on some sqlite builds
                pass
    except Exception:
        pass

    # enrolamiento
    cur.execute('''
    CREATE TABLE IF NOT EXISTS enrolar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER,
        tarjeta_uid TEXT,
        tarjeta_id INTEGER,
        codigo_ingreso TEXT,
        perfil_acceso_lab_id INTEGER,
        estado INTEGER DEFAULT 1,
        fecha_de_registro TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(persona_id) REFERENCES personas(id),
        FOREIGN KEY(perfil_acceso_lab_id) REFERENCES perfil_acceso_lab(id),
        FOREIGN KEY(tarjeta_id) REFERENCES tarjetas(id)
    )
    ''')

    # Ensure enrolar table has 'tarjeta_id' column and migrate values from 'tarjeta_uid' when possible
    try:
        cur.execute("PRAGMA table_info(enrolar)")
        cols = [r['name'] for r in cur.fetchall()]
        if 'tarjeta_id' not in cols:
            try:
                cur.execute('ALTER TABLE enrolar ADD COLUMN tarjeta_id INTEGER')
                # If there is an existing tarjeta_uid column, try to populate tarjeta_id
                if 'tarjeta_uid' in cols:
                    try:
                        cur.execute(
                            """
                            UPDATE enrolar
                            SET tarjeta_id = (
                                SELECT id FROM tarjetas WHERE tarjetas.uid = enrolar.tarjeta_uid
                            )
                            WHERE tarjeta_uid IS NOT NULL
                            """
                        )
                    except Exception:
                        # best-effort population; ignore failures
                        pass
            except Exception:
                # Some SQLite builds may restrict ALTER TABLE; ignore on failure
                pass
    except Exception:
        pass

    # Ensure enrolar table has 'accion' column (for action tracking)
    try:
        cur.execute("PRAGMA table_info(enrolar)")
        cols = [r['name'] for r in cur.fetchall()]
        if 'accion' not in cols:
            try:
                cur.execute('ALTER TABLE enrolar ADD COLUMN accion TEXT DEFAULT "activo"')
            except Exception:
                pass
    except Exception:
        pass

    # tipos de movimiento
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tipo_movimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movimiento TEXT NOT NULL UNIQUE,
        descripcion TEXT NOT NULL,
        estado INTEGER DEFAULT 1
    )
    ''')

    # Seed default movement types if empty
    try:
        cur.execute("SELECT COUNT(*) FROM tipo_movimiento")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO tipo_movimiento (movimiento, descripcion, estado) VALUES (?, ?, ?)", ('entrada', 'Registro entrada', 1))
            cur.execute("INSERT INTO tipo_movimiento (movimiento, descripcion, estado) VALUES (?, ?, ?)", ('salida', 'Registro de salida', 1))
            conn.commit()
    except Exception:
        # If insert fails (e.g., duplicates exist), continue
        pass

    cur.execute('''
    CREATE TABLE IF NOT EXISTS tipo_dispositivo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        estado INTEGER DEFAULT 1
    )
    ''')

    # tipos de registro
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tipo_registro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        perfil_fk INTEGER,
        estado INTEGER DEFAULT 1,
        FOREIGN KEY(perfil_fk) REFERENCES perfil_acceso_lab(id)
    )
    ''')

    # Seed default registro types if empty
    try:
        cur.execute("SELECT COUNT(*) FROM tipo_registro")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO tipo_registro (id, nombre, perfil_fk, estado) VALUES (?, ?, ?, ?)", (1, 'pin', 1, 1))
            cur.execute("INSERT INTO tipo_registro (id, nombre, perfil_fk, estado) VALUES (?, ?, ?, ?)", (2, 'tarjeta', 1, 1))
            conn.commit()
    except Exception:
        # If insert fails (e.g., duplicates exist), continue
        pass

    # registro de accesos
    cur.execute('''
    CREATE TABLE IF NOT EXISTS registro_acceso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrolar_id INTEGER,
        tarjeta_uid TEXT,
        codigo_ingreso TEXT,
        fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
        tipo_movimiento_id INTEGER,
        tipo_dispositivo_id INTEGER,
        resultado TEXT,
        credencial TEXT,
        descripcion TEXT,
        estado INTEGER DEFAULT 1,
        FOREIGN KEY(enrolar_id) REFERENCES enrolar(id),
        FOREIGN KEY(tipo_movimiento_id) REFERENCES tipo_movimiento(id),
        FOREIGN KEY(tipo_dispositivo_id) REFERENCES tipo_dispositivo(id)
    )
    ''')

    # Ensure registro_acceso has resultado and credencial columns (for existing DBs)
    try:
        cur.execute("PRAGMA table_info(registro_acceso)")
        cols = [r['name'] for r in cur.fetchall()]
        if 'resultado' not in cols:
            try:
                cur.execute('ALTER TABLE registro_acceso ADD COLUMN resultado TEXT')
            except Exception:
                pass
        if 'credencial' not in cols:
            try:
                cur.execute('ALTER TABLE registro_acceso ADD COLUMN credencial TEXT')
            except Exception:
                pass
        if 'enrolar_id' not in cols:
            try:
                cur.execute('ALTER TABLE registro_acceso ADD COLUMN enrolar_id INTEGER')
            except Exception:
                pass
    except Exception:
        pass

    # dispositivos (ESP32)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        activo INTEGER DEFAULT 1,
        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # historiales y bitácora
    cur.execute('''
    CREATE TABLE IF NOT EXISTS historial_acciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modulo TEXT,
        entidad_id INTEGER,
        entidad_tipo TEXT,
        accion TEXT,
        usuario TEXT,
        descripcion TEXT,
        documento_identidad TEXT,
        fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    try:
        cur.execute('ALTER TABLE historial_acciones ADD COLUMN documento_identidad TEXT')
    except Exception:
        pass

    try:
        cur.execute('''
            UPDATE historial_acciones
            SET documento_identidad = (
                SELECT p.documento_identidad
                FROM personas p
                WHERE p.id = historial_acciones.entidad_id
            )
            WHERE entidad_tipo = 'persona' AND documento_identidad IS NULL
        ''')
        conn.commit()
    except Exception:
        pass

    cur.execute('''
    CREATE TABLE IF NOT EXISTS historial_tarjetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarjeta_id INTEGER,
        uid TEXT,
        nombre_completo TEXT,
        accion TEXT,
        ejecutado_por TEXT,
        descripcion TEXT,
        fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(tarjeta_id) REFERENCES tarjetas(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS bitacora (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_sistema_id INTEGER,
        estado INTEGER DEFAULT 1,
        FOREIGN KEY(usuario_sistema_id) REFERENCES usuario_sistema(id)
    )
    ''')

    conn.commit()
    cur.close()


def log_action(connection, modulo, entidad_id=None, entidad_tipo=None,
               accion=None, usuario=None, descripcion=None, documento_identidad=None):
    """Inserta una fila de auditoría en `historial_acciones`."""
    if documento_identidad is None and entidad_tipo == 'persona' and entidad_id is not None:
        inner_cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            inner_cursor.execute(f"SELECT documento_identidad FROM personas WHERE id = {placeholder}", (entidad_id,))
            row = inner_cursor.fetchone()
            if row:
                documento_identidad = row[0] if isinstance(row, (list, tuple)) else (row.get('documento_identidad') if hasattr(row, 'get') else None)
        except Exception:
            pass
        finally:
            try:
                inner_cursor.close()
            except Exception:
                pass

    sql = '''
    INSERT INTO historial_acciones
    (modulo, entidad_id, entidad_tipo, accion, usuario, descripcion, documento_identidad)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    if connection.__class__.__module__.startswith('sqlite3'):
        sql = sql.replace('%s', '?')
    cursor = connection.cursor()
    try:
        cursor.execute(sql, (modulo, entidad_id, entidad_tipo, accion, usuario, descripcion, documento_identidad))
        connection.commit()
    finally:
        try:
            cursor.close()
        except Exception:
            pass