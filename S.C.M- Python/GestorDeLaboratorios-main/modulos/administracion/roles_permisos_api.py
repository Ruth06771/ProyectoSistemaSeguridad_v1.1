from flask import Blueprint, request, jsonify
from config.db import get_connection, log_action
import traceback

roles_api = Blueprint('roles_api', __name__)


def _placeholder_for(conn):
    return '?' if conn.__class__.__module__.startswith('sqlite3') else '%s'


# ============================================================
# ENDPOINTS DE ROLES (usando tabla rol_sistema)
# ============================================================

@roles_api.route('/api/roles', methods=['GET'])
def listar_roles():
    """Listar todos los roles del sistema"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, nombre FROM rol_sistema WHERE estado = 1')
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                data = [dict(r) for r in rows]
            else:
                data = [{'id': r[0], 'nombre': r[1]} for r in rows] if rows else []
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'query_failed', 'message': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ============================================================
# ENDPOINTS DE PERMISOS por ROL (usando tablas permisos y detalle_del_permiso)
# ============================================================

@roles_api.route('/api/permisos-modulos', methods=['GET'])
def listar_permisos_modulos():
    """Listar todos los permisos (módulos) disponibles"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, nombre FROM permisos')
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                data = [dict(r) for r in rows]
            else:
                data = [{'id': r[0], 'nombre': r[1]} for r in rows] if rows else []
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'query_failed', 'message': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@roles_api.route('/api/roles/<int:role_id>/permisos', methods=['GET'])
def listar_permisos_del_rol(role_id):
    """Listar permisos asignados a un rol específico"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            # Obtener lista completa de módulos siempre
            cur.execute('SELECT id, nombre FROM permisos')
            modules = cur.fetchall()
            assigned_map = {}
            cur.execute('SELECT permiso_id, ver, crear, editar, eliminar FROM detalle_del_permiso WHERE rol_id = ? AND estado = 1', (role_id,))
            assigned_rows = cur.fetchall()
            for row in assigned_rows:
                permiso_id = row['permiso_id'] if hasattr(row, 'keys') else row[0]
                ver = row['ver'] if hasattr(row, 'keys') else row[1]
                crear = row['crear'] if hasattr(row, 'keys') else row[2]
                editar = row['editar'] if hasattr(row, 'keys') else row[3]
                eliminar = row['eliminar'] if hasattr(row, 'keys') else row[4]
                assigned_map[permiso_id] = {
                    'ver': bool(ver),
                    'crear': bool(crear),
                    'editar': bool(editar),
                    'eliminar': bool(eliminar)
                }

            data = []
            for row in modules:
                permiso_id = row['id'] if hasattr(row, 'keys') else row[0]
                permiso_nombre = row['nombre'] if hasattr(row, 'keys') else row[1]
                permiso_flags = assigned_map.get(permiso_id, {
                    'ver': False,
                    'crear': False,
                    'editar': False,
                    'eliminar': False
                })
                assigned = permiso_flags['ver'] or permiso_flags['crear'] or permiso_flags['editar'] or permiso_flags['eliminar']
                data.append({
                    'id': permiso_id,
                    'nombre': permiso_nombre,
                    'assigned': assigned,
                    'ver': permiso_flags['ver'],
                    'crear': permiso_flags['crear'],
                    'editar': permiso_flags['editar'],
                    'eliminar': permiso_flags['eliminar'],
                })
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'query_failed', 'message': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@roles_api.route('/api/roles/<int:role_id>/permisos', methods=['POST'])
def asignar_permisos_a_rol(role_id):
    """Asignar o actualizar permisos de un rol. Recibe matriz de permisos por acción."""
    data = request.get_json() or {}
    permiso_matrix = data.get('permiso_matrix')
    permiso_ids = data.get('permiso_ids', [])

    if permiso_matrix is None:
        # Compatibilidad con clientes antiguos que envían solo permiso_ids
        if not isinstance(permiso_ids, list):
            return jsonify({'error': 'invalid_permiso_ids_format'}), 400
        permiso_matrix = [{
            'id': pid,
            'ver': 1,
            'crear': 1,
            'editar': 1,
            'eliminar': 1
        } for pid in permiso_ids]

    if not isinstance(permiso_matrix, list):
        return jsonify({'error': 'invalid_permiso_matrix_format'}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            # Eliminar cualquier asignación previa del rol
            cur.execute('DELETE FROM detalle_del_permiso WHERE rol_id = ?', (role_id,))

            # Insertar la configuración de permisos por acción
            for permiso_entry in permiso_matrix:
                permiso_id = permiso_entry.get('id')
                if permiso_id is None:
                    continue
                ver = 1 if permiso_entry.get('ver') else 0
                crear = 1 if permiso_entry.get('crear') else 0
                editar = 1 if permiso_entry.get('editar') else 0
                eliminar = 1 if permiso_entry.get('eliminar') else 0
                has_any = bool(ver or crear or editar or eliminar)
                if not has_any:
                    continue
                try:
                    cur.execute(
                        '''
                        INSERT INTO detalle_del_permiso (permiso_id, estado, ver, crear, editar, eliminar, rol_id)
                        VALUES (?, 1, ?, ?, ?, ?, ?)
                        ''',
                        (permiso_id, ver, crear, editar, eliminar, role_id)
                    )
                except Exception:
                    # Ignorar duplicados o errores de integridad referencial
                    pass

            conn.commit()
            try:
                log_action(conn, 'permisos', entidad_id=role_id, entidad_tipo='rol', accion='update_permisos', usuario=None, descripcion=f'Actualizados permisos para rol {role_id}')
            except Exception:
                pass
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'update_failed', 'message': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@roles_api.route('/api/roles/<int:role_id>/permisos/<int:permiso_id>', methods=['DELETE'])
def quitar_permiso_de_rol(role_id, permiso_id):
    """Quitar un permiso específico de un rol"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute('DELETE FROM detalle_del_permiso WHERE rol_id = ? AND permiso_id = ?', (role_id, permiso_id))
            conn.commit()
            try:
                log_action(conn, 'permisos', entidad_id=None, entidad_tipo='rol_permiso', accion='delete', usuario=None, descripcion=f'Quitado permiso {permiso_id} de rol {role_id}')
            except Exception:
                pass
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'delete_failed', 'message': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass
