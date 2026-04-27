from flask import Blueprint, request, jsonify
from config.db import get_connection, log_action
import traceback

roles_api = Blueprint('roles_api', __name__)


def _placeholder_for(conn):
    return '?' if conn.__class__.__module__.startswith('sqlite3') else '%s'


@roles_api.route('/api/roles', methods=['GET'])
def listar_roles():
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, nombre, descripcion FROM roles')
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                data = [dict(r) for r in rows]
            else:
                data = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/roles', methods=['POST'])
def crear_rol():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    if not nombre:
        return jsonify({'error': 'missing_name'}), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            ph = _placeholder_for(conn)
            sql = f'INSERT INTO roles (nombre, descripcion) VALUES ({ph}, {ph})'
            cur.execute(sql, (nombre, descripcion))
            conn.commit()
            log_action(conn, 'roles', entidad_id=cur.lastrowid if hasattr(cur, 'lastrowid') else None, entidad_tipo='rol', accion='create', usuario=None, descripcion=f'Creado rol {nombre}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'insert_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/roles/<int:id>', methods=['DELETE'])
def eliminar_rol(id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            ph = _placeholder_for(conn)
            cur.execute(f'DELETE FROM roles WHERE id = {ph}', (id,))
            conn.commit()
            log_action(conn, 'roles', entidad_id=id, entidad_tipo='rol', accion='delete', usuario=None, descripcion=f'Eliminado rol id={id}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'delete_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/permisos', methods=['GET'])
def listar_permisos():
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, nombre, descripcion FROM permisos')
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                data = [dict(r) for r in rows]
            else:
                data = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/permisos', methods=['POST'])
def crear_permiso():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    if not nombre:
        return jsonify({'error': 'missing_name'}), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            ph = _placeholder_for(conn)
            sql = f'INSERT INTO permisos (nombre, descripcion) VALUES ({ph}, {ph})'
            cur.execute(sql, (nombre, descripcion))
            conn.commit()
            log_action(conn, 'permisos', entidad_id=cur.lastrowid if hasattr(cur, 'lastrowid') else None, entidad_tipo='permiso', accion='create', usuario=None, descripcion=f'Creado permiso {nombre}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'insert_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/permisos/<int:id>', methods=['DELETE'])
def eliminar_permiso(id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            ph = _placeholder_for(conn)
            cur.execute(f'DELETE FROM permisos WHERE id = {ph}', (id,))
            conn.commit()
            log_action(conn, 'permisos', entidad_id=id, entidad_tipo='permiso', accion='delete', usuario=None, descripcion=f'Eliminado permiso id={id}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'delete_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/roles/<int:role_id>/permisos', methods=['GET'])
def listar_permisos_del_rol(role_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            # join permisos via role_permisos
            cur.execute('SELECT p.id, p.nombre, p.descripcion FROM permisos p JOIN role_permisos rp ON rp.permiso_id = p.id WHERE rp.role_id = ?', (role_id,))
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                data = [dict(r) for r in rows]
            else:
                data = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/roles/<int:role_id>/permisos', methods=['POST'])
def asignar_permiso_a_rol(role_id):
    data = request.get_json() or {}
    permiso_id = data.get('permiso_id')
    if not permiso_id:
        return jsonify({'error': 'missing_permiso_id'}), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            # insert ignore-like behavior: try insert and ignore duplicate key
            try:
                cur.execute('INSERT INTO role_permisos (role_id, permiso_id) VALUES (?, ?)', (role_id, permiso_id))
                conn.commit()
            except Exception:
                # could be duplicate primary key; ignore
                pass
            log_action(conn, 'role_permisos', entidad_id=None, entidad_tipo='role_permiso', accion='assign', usuario=None, descripcion=f'Asignado permiso {permiso_id} a rol {role_id}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'assign_failed'}), 500
    finally:
        conn.close()


@roles_api.route('/api/roles/<int:role_id>/permisos/<int:permiso_id>', methods=['DELETE'])
def quitar_permiso_de_rol(role_id, permiso_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('DELETE FROM role_permisos WHERE role_id = ? AND permiso_id = ?', (role_id, permiso_id))
            conn.commit()
            log_action(conn, 'role_permisos', entidad_id=None, entidad_tipo='role_permiso', accion='unassign', usuario=None, descripcion=f'Quitado permiso {permiso_id} de rol {role_id}')
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'delete_failed'}), 500
    finally:
        conn.close()
