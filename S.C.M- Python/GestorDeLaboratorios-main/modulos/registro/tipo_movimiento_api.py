from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import sqlite3

tipo_movimiento_api = Blueprint('tipo_movimiento_api', __name__)


# Listar todos los tipos de movimiento
@tipo_movimiento_api.route('/api/tipo_movimiento', methods=['GET'])
def listar_tipo_movimiento():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_movimiento ORDER BY id DESC")
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                movimientos = [dict(r) for r in rows]
            else:
                movimientos = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(movimientos)
    finally:
        connection.close()


# Crear tipo de movimiento
@tipo_movimiento_api.route('/api/tipo_movimiento', methods=['POST'])
def crear_tipo_movimiento():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
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
            sql = "INSERT INTO tipo_movimiento (nombre, estado) VALUES (?, ?)"
            cursor.execute(sql, (nombre, estado))
            connection.commit()
            try:
                log_action(connection, 'tipo_movimiento', entidad_id=cursor.lastrowid, entidad_tipo='tipo_movimiento', 
                          accion='create', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Creado tipo de movimiento: {nombre}")
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


# Obtener tipo de movimiento por ID
@tipo_movimiento_api.route('/api/tipo_movimiento/<int:id>', methods=['GET'])
def obtener_tipo_movimiento(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_movimiento WHERE id = ?", (id,))
            mov = cursor.fetchone()
            if mov and hasattr(mov, 'keys'):
                mov = dict(mov)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        if not mov:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(mov)
    finally:
        connection.close()


# Actualizar tipo de movimiento
@tipo_movimiento_api.route('/api/tipo_movimiento/<int:id>', methods=['PUT'])
def actualizar_tipo_movimiento(id):
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
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
            sql = "UPDATE tipo_movimiento SET nombre = ?, estado = ? WHERE id = ?"
            cursor.execute(sql, (nombre, estado, id))
            connection.commit()
            try:
                log_action(connection, 'tipo_movimiento', entidad_id=id, entidad_tipo='tipo_movimiento', 
                          accion='update', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Actualizado tipo de movimiento id={id}")
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


# Eliminar tipo de movimiento
@tipo_movimiento_api.route('/api/tipo_movimiento/<int:id>', methods=['DELETE'])
def eliminar_tipo_movimiento(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM tipo_movimiento WHERE id = ?", (id,))
            connection.commit()
            try:
                log_action(connection, 'tipo_movimiento', entidad_id=id, entidad_tipo='tipo_movimiento', 
                          accion='delete', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Eliminado tipo de movimiento id={id}")
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
