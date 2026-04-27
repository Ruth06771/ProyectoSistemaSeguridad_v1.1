from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action

tipo_dispositivo_api = Blueprint('tipo_dispositivo_api', __name__)


# Listar todos los tipos de dispositivo
@tipo_dispositivo_api.route('/api/tipo_dispositivo', methods=['GET'])
def listar_tipo_dispositivo():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_dispositivo ORDER BY id DESC")
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                items = [dict(r) for r in rows]
            else:
                items = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(items)
    finally:
        connection.close()


# Crear tipo de dispositivo
@tipo_dispositivo_api.route('/api/tipo_dispositivo', methods=['POST'])
def crear_tipo_dispositivo():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    estado = data.get('estado', 1)

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = "INSERT INTO tipo_dispositivo (nombre, estado) VALUES (?, ?)"
            cursor.execute(sql, (nombre, estado))
            connection.commit()
            try:
                log_action(connection, 'tipo_dispositivo', entidad_id=cursor.lastrowid, entidad_tipo='tipo_dispositivo', 
                          accion='create', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Creado tipo de dispositivo: {nombre}")
            except Exception:
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True, 'id': cursor.lastrowid})
    finally:
        connection.close()


# Obtener por ID
@tipo_dispositivo_api.route('/api/tipo_dispositivo/<int:id>', methods=['GET'])
def obtener_tipo_dispositivo(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_dispositivo WHERE id = ?", (id,))
            item = cursor.fetchone()
            if item and hasattr(item, 'keys'):
                item = dict(item)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        if not item:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(item)
    finally:
        connection.close()


# Actualizar
@tipo_dispositivo_api.route('/api/tipo_dispositivo/<int:id>', methods=['PUT'])
def actualizar_tipo_dispositivo(id):
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    estado = data.get('estado', 1)

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = "UPDATE tipo_dispositivo SET nombre = ?, estado = ? WHERE id = ?"
            cursor.execute(sql, (nombre, estado, id))
            connection.commit()
            try:
                log_action(connection, 'tipo_dispositivo', entidad_id=id, entidad_tipo='tipo_dispositivo', 
                          accion='update', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Actualizado tipo_dispositivo id={id}")
            except Exception:
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    finally:
        connection.close()


# Eliminar
@tipo_dispositivo_api.route('/api/tipo_dispositivo/<int:id>', methods=['DELETE'])
def eliminar_tipo_dispositivo(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM tipo_dispositivo WHERE id = ?", (id,))
            connection.commit()
            try:
                log_action(connection, 'tipo_dispositivo', entidad_id=id, entidad_tipo='tipo_dispositivo', 
                          accion='delete', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Eliminado tipo_dispositivo id={id}")
            except Exception:
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    finally:
        connection.close()
