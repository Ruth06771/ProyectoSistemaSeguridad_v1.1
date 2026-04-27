from flask import Blueprint, request, jsonify, session
from config.db import get_connection
from config.db import log_action
import sqlite3

tarjetas_api = Blueprint('tarjetas_api', __name__)


# Listar tarjetas
@tarjetas_api.route('/api/tarjetas', methods=['GET'])
def listar_tarjetas():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM tarjetas")
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                tarjetas = [dict(r) for r in rows]
            else:
                tarjetas = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(tarjetas)
    finally:
        connection.close()

# Registrar tarjeta
@tarjetas_api.route('/api/tarjetas', methods=['POST'])
def registrar_tarjeta():
    data = request.get_json()
    campos = ['uid', 'nombre_completo', 'correo', 'pin', 'estado']
    valores = [data.get(campo) for campo in campos]
    # Server-side validation for PIN: must be exactly 8 digits
    pin = (data.get('pin') or '')
    if not isinstance(pin, str):
        pin = str(pin)
    pin = pin.strip()
    import re
    if not re.fullmatch(r"\d{8}", pin):
        return jsonify({'error': 'invalid_pin', 'message': 'El PIN debe contener exactamente 8 dígitos'}), 400
    # ensure valores has cleaned pin
    valores[-2] = pin
    # Handle estado: default to 1 (activo) if not provided
    estado = data.get('estado', 1)
    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)
    valores[-1] = estado
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = """
                INSERT INTO tarjetas (uid, nombre_completo, correo, pin, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            if connection.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            try:
                cursor.execute(sql, valores)
                connection.commit()
            except Exception as e:
                # Detect duplicate uid for sqlite and pymysql
                if isinstance(e, sqlite3.IntegrityError) or 'UNIQUE constraint failed' in str(e) or 'Duplicate entry' in str(e):
                    return jsonify({'error': 'duplicate_uid', 'message': 'El UID ya existe'}), 400
                raise
            # Log action (audit)
            try:
                log_action(connection, 'tarjetas', entidad_id=cursor.lastrowid if hasattr(cursor, 'lastrowid') else None, entidad_tipo='tarjeta', accion='create', usuario=session.get('usuario') if session else None, descripcion=f"Creada tarjeta uid={valores[0]}")
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

# Obtener tarjeta por ID
@tarjetas_api.route('/api/tarjetas/<int:id>', methods=['GET'])
def obtener_tarjeta(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (id,)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cursor.execute(f"SELECT * FROM tarjetas WHERE id = {placeholder}", params)
            tarjeta = cursor.fetchone()
            if tarjeta and hasattr(tarjeta, 'keys'):
                tarjeta = dict(tarjeta)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        if not tarjeta:
            return jsonify({'error': 'No encontrada'}), 404
        return jsonify(tarjeta)
    finally:
        connection.close()

# Editar tarjeta
@tarjetas_api.route('/api/tarjetas/<int:id>', methods=['PUT'])
def editar_tarjeta(id):
    data = request.get_json()
    campos = ['uid', 'nombre_completo', 'correo', 'pin', 'estado']
    valores = [data.get(campo) for campo in campos]
    # Server-side validation for PIN: must be exactly 8 digits
    pin = (data.get('pin') or '')
    if not isinstance(pin, str):
        pin = str(pin)
    pin = pin.strip()
    import re
    if not re.fullmatch(r"\d{8}", pin):
        return jsonify({'error': 'invalid_pin', 'message': 'El PIN debe contener exactamente 8 dígitos'}), 400
    valores[-2] = pin
    # Handle estado: default to 1 if not provided
    estado = data.get('estado', 1)
    if estado not in (0, 1, '0', '1'):
        estado = 1
    estado = int(estado)
    valores[-1] = estado
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = """
                UPDATE tarjetas SET uid=%s, nombre_completo=%s, correo=%s, pin=%s, estado=%s
                WHERE id=%s
            """
            if connection.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            cursor.execute(sql, valores + [id])
            connection.commit()
            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion='update', usuario=session.get('usuario') if session else None, descripcion=f"Actualizada tarjeta id={id}")
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

# Eliminar tarjeta
@tarjetas_api.route('/api/tarjetas/<int:id>', methods=['DELETE'])
def eliminar_tarjeta(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (id,)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cursor.execute(f"DELETE FROM tarjetas WHERE id = {placeholder}", params)
            connection.commit()
            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion='delete', usuario=session.get('usuario') if session else None, descripcion=f"Eliminada tarjeta id={id}")
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


# Buscar tarjetas por nombre o correo de persona (útil para enrolar: devolver UID+PIN por persona)
@tarjetas_api.route('/api/tarjetas/search_by_persona', methods=['GET'])
def buscar_tarjetas_por_persona():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            like = f"%{q}%"
            # search by nombre_completo or correo
            sql = f"SELECT * FROM tarjetas WHERE nombre_completo LIKE {placeholder} OR correo LIKE {placeholder}"
            params = (like, like)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                tarjetas = [dict(r) for r in rows]
            else:
                tarjetas = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(tarjetas)
    finally:
        connection.close()
