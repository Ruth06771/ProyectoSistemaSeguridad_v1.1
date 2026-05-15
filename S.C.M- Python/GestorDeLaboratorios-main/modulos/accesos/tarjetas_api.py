from flask import Blueprint, request, jsonify, session
from config.db import get_connection
from config.db import log_action
import sqlite3

tarjetas_api = Blueprint('tarjetas_api', __name__)


def normalize_tarjeta(tarjeta):
    if tarjeta is None:
        return None
    if hasattr(tarjeta, 'keys'):
        tarjeta = dict(tarjeta)
    if isinstance(tarjeta, dict):
        if 'estado' in tarjeta and 'activo' not in tarjeta:
            tarjeta['activo'] = tarjeta['estado']
    return tarjeta


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
                tarjetas = [normalize_tarjeta(dict(r)) for r in rows]
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
            try:
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, datetime('now'))
                """
                if not connection.__class__.__module__.startswith('sqlite3'):
                    sql_hist = sql_hist.replace("datetime('now')", 'NOW()')
                cursor.execute(sql_hist, (
                    cursor.lastrowid if hasattr(cursor, 'lastrowid') else None,
                    str(valores[0] or ''),
                    str(valores[1] or ''),
                    'creada',
                    session.get('usuario') if session else None,
                    f'Tarjeta creada uid={valores[0]}'
                ))
                connection.commit()
            except Exception:
                pass
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
        return jsonify(normalize_tarjeta(tarjeta))
    finally:
        connection.close()

# Editar tarjeta
@tarjetas_api.route('/api/tarjetas/<int:id>', methods=['PUT', 'PATCH'])
def editar_tarjeta(id):
    data = request.get_json()
    if request.method == 'PATCH':
        activo = data.get('activo')
        if activo in (1, '1', True, 'true', 'True'):
            estado = 1
        elif activo in (0, '0', False, 'false', 'False'):
            estado = 0
        else:
            return jsonify({'error': 'invalid_activo', 'message': 'Campo activo inválido'}), 400

        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                placeholder = '%s'
                params = (estado, id)
                if connection.__class__.__module__.startswith('sqlite3'):
                    placeholder = '?'
                cursor.execute(f"UPDATE tarjetas SET estado = {placeholder} WHERE id = {placeholder}", params)
                connection.commit()
                try:
                    log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion='update', usuario=session.get('usuario') if session else None, descripcion=f"Actualizado estado de tarjeta id={id} a {estado}")
                except Exception:
                    pass
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            connection.close()
        return jsonify({'success': True})

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
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, datetime('now'))
                """
                if not connection.__class__.__module__.startswith('sqlite3'):
                    sql_hist = sql_hist.replace("datetime('now')", 'NOW()')
                cursor.execute(sql_hist, (
                    id,
                    str(data.get('uid') or ''),
                    str(data.get('nombre_completo') or ''),
                    'editada',
                    session.get('usuario') if session else None,
                    f'Tarjeta editada id={id}'
                ))
                connection.commit()
            except Exception:
                pass
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
            cursor.execute(f"SELECT uid, nombre_completo FROM tarjetas WHERE id = {placeholder}", params)
            tarjeta = cursor.fetchone()
            uid = None
            nombre_completo = None
            if tarjeta:
                if hasattr(tarjeta, 'keys'):
                    uid = tarjeta.get('uid')
                    nombre_completo = tarjeta.get('nombre_completo')
                else:
                    uid = tarjeta[0] if len(tarjeta) > 0 else None
                    nombre_completo = tarjeta[1] if len(tarjeta) > 1 else None
            cursor.execute(f"DELETE FROM tarjetas WHERE id = {placeholder}", params)
            connection.commit()
            try:
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, datetime('now'))
                """
                if not connection.__class__.__module__.startswith('sqlite3'):
                    sql_hist = sql_hist.replace("datetime('now')", 'NOW()')
                cursor.execute(sql_hist, (
                    id,
                    uid,
                    nombre_completo,
                    'eliminada',
                    session.get('usuario') if session else None,
                    f'Tarjeta eliminada id={id}'
                ))
                connection.commit()
            except Exception:
                pass
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
                tarjetas = [normalize_tarjeta(dict(r)) for r in rows]
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


# Registrar acción en tarjeta (Alta, Baja, Eliminada)
@tarjetas_api.route('/api/tarjetas/<int:id>/accion', methods=['POST'])
def registrar_accion_tarjeta(id):
    data = request.get_json()
    accion = data.get('accion', '').strip().lower()
    
    if accion not in ('alta', 'baja', 'eliminada'):
        return jsonify({'error': 'Acción inválida'}), 400
    
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            
            # Obtener datos de la tarjeta primero
            cursor.execute(f"SELECT * FROM tarjetas WHERE id = {placeholder}", (id,))
            tarjeta = cursor.fetchone()
            if not tarjeta:
                return jsonify({'error': 'Tarjeta no encontrada'}), 404
            
            # Convertir a dict si es necesario
            if hasattr(tarjeta, 'keys'):
                tarjeta_dict = dict(tarjeta)
            else:
                # Si es tupla, crear dict manualmente (esto es un fallback)
                tarjeta_dict = {'id': tarjeta[0], 'uid': tarjeta[1]}
            
            uid = tarjeta_dict.get('uid')
            usuario = session.get('usuario') if session else None
            
            # Procesar la acción
            if accion == 'eliminada':
                # Eliminar tarjeta
                cursor.execute(f"DELETE FROM tarjetas WHERE id = {placeholder}", (id,))
                connection.commit()
                # Registrar en historial
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, datetime('now'))
                """
                if not connection.__class__.__module__.startswith('sqlite3'):
                    sql_hist = sql_hist.replace("datetime('now')", 'NOW()')
                cursor.execute(sql_hist, (uid, None, 'eliminada', usuario, f'Tarjeta eliminada'))
                connection.commit()
            else:
                # Alta o Baja: actualizar estado
                new_estado = 1 if accion == 'alta' else 0
                cursor.execute(
                    f"UPDATE tarjetas SET estado = {placeholder} WHERE id = {placeholder}",
                    (new_estado, id)
                )
                connection.commit()
                # Registrar en historial
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, datetime('now'))
                """
                if not connection.__class__.__module__.startswith('sqlite3'):
                    sql_hist = sql_hist.replace("datetime('now')", 'NOW()')
                cursor.execute(sql_hist, (id, uid, None, accion, usuario, f'Tarjeta marcada como {accion}'))
                connection.commit()
            
            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', 
                          accion=accion, usuario=usuario, descripcion=f"Acción {accion} en tarjeta id={id}")
            except Exception:
                pass
            
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        
        return jsonify({'success': True, 'accion': accion})
    finally:
        connection.close()
