from flask import Blueprint, request, jsonify, session
from config.db import get_connection
import traceback

usuarios_api = Blueprint('usuarios_api', __name__)


def try_get_connection():
    try:
        conn = get_connection()
        return conn, None
    except Exception as e:
        return None, str(e)


@usuarios_api.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """Devuelve lista de personas con campos básicos y rol.
    Filtra por personas activos para sincronización correcta con eliminaciones."""
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.ver', False):
        return jsonify({'error': 'forbidden', 'message': 'Acceso denegado'}), 403

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            # Selecciona SOLO personas con estado = 1 para sincronización correcta
            # Excluye personas que tengan usuario_sistema asociado con estado = 0
            sql = ("SELECT DISTINCT p.id, p.nombre_completo, p.correo, p.rol "
                   "FROM personas p "
                   "WHERE p.estado = 1 "
                   "ORDER BY p.nombre_completo")
            cursor.execute(sql)
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                usuarios = [dict(r) for r in rows]
            else:
                usuarios = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(usuarios)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        connection.close()


@usuarios_api.route('/api/usuarios/<int:id>/rol', methods=['PUT'])
def actualizar_rol(id):
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.editar', False):
        return jsonify({'error': 'forbidden', 'message': 'Acceso denegado'}), 403

    data = request.get_json() or {}
    rol = data.get('rol')
    allowed = ('administrador', 'docente', 'estudiante', 'auxiliar', 'invitado')
    if rol not in allowed:
        return jsonify({'error': 'invalid_role', 'allowed': allowed}), 400

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (rol, id)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            sql = f"UPDATE personas SET rol = {placeholder} WHERE id = {placeholder}"
            # For sqlite placeholder replacement above produced '?' for both; for pymysql we still used %s
            if connection.__class__.__module__.startswith('sqlite3'):
                cursor.execute("UPDATE personas SET rol = ? WHERE id = ?", params)
            else:
                cursor.execute("UPDATE personas SET rol = %s WHERE id = %s", params)
            connection.commit()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'update_failed'}), 500
    finally:
        connection.close()
