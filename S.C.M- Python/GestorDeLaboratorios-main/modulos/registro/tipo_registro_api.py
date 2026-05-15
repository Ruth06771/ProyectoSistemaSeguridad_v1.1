from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import sqlite3

tipo_registro_api = Blueprint('tipo_registro_api', __name__)


# Listar tipos de registro
@tipo_registro_api.route('/api/tipo_registro', methods=['GET'])
def listar_tipo_registro():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_registro ORDER BY id DESC")
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                registros = [dict(r) for r in rows]
            else:
                registros = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(registros)
    finally:
        connection.close()


# Crear tipo de registro
@tipo_registro_api.route('/api/tipo_registro', methods=['POST'])
def crear_tipo_registro():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    perfil_fk = data.get('perfil_fk')
    estado = data.get('estado', 1)
    
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    if perfil_fk is None:
        return jsonify({'error': 'Perfil FK es obligatorio'}), 400
    
    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)
    
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = "INSERT INTO tipo_registro (nombre, perfil_fk, estado) VALUES (?, ?, ?)"
            cursor.execute(sql, (nombre, perfil_fk, estado))
            connection.commit()
            try:
                log_action(connection, 'tipo_registro', entidad_id=cursor.lastrowid, entidad_tipo='tipo_registro', 
                          accion='create', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Creado tipo de registro: {nombre}")
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


# Obtener tipo de registro por ID
@tipo_registro_api.route('/api/tipo_registro/<int:id>', methods=['GET'])
def obtener_tipo_registro(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_registro WHERE id = ?", (id,))
            reg = cursor.fetchone()
            if reg and hasattr(reg, 'keys'):
                reg = dict(reg)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        if not reg:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(reg)
    finally:
        connection.close()


# Actualizar tipo de registro
@tipo_registro_api.route('/api/tipo_registro/<int:id>', methods=['PUT'])
def actualizar_tipo_registro(id):
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    perfil_fk = data.get('perfil_fk')
    estado = data.get('estado', 1)
    
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    if perfil_fk is None:
        return jsonify({'error': 'Perfil FK es obligatorio'}), 400
    
    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)
    
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = "UPDATE tipo_registro SET nombre = ?, perfil_fk = ?, estado = ? WHERE id = ?"
            cursor.execute(sql, (nombre, perfil_fk, estado, id))
            connection.commit()
            try:
                log_action(connection, 'tipo_registro', entidad_id=id, entidad_tipo='tipo_registro', 
                          accion='update', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Actualizado tipo de registro id={id}")
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


# Eliminar tipo de registro
@tipo_registro_api.route('/api/tipo_registro/<int:id>', methods=['DELETE'])
def eliminar_tipo_registro(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM tipo_registro WHERE id = ?", (id,))
            connection.commit()
            try:
                log_action(connection, 'tipo_registro', entidad_id=id, entidad_tipo='tipo_registro', 
                          accion='delete', usuario=session.get('usuario') if session else None, 
                          descripcion=f"Eliminado tipo de registro id={id}")
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