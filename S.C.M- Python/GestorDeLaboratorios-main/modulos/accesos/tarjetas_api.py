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
            cursor.execute("SELECT * FROM tarjetas WHERE estado = 1")
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
            
            # Obtener ID de la tarjeta creada
            tarjeta_id = None
            try:
                if hasattr(cursor, 'lastrowid'):
                    tarjeta_id = cursor.lastrowid
            except Exception:
                pass
            
            # Registrar en historial
            try:
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                """
                usuario = session.get('usuario') if session else 'Sistema'
                cursor.execute(sql_hist, (
                    tarjeta_id,
                    str(valores[0] or ''),
                    str(valores[1] or ''),
                    'creada',
                    usuario,
                    f'Tarjeta creada: {valores[1]} ({valores[0]})'
                ))
                connection.commit()
            except Exception as hist_err:
                print(f"[ERROR] No se registró creación en historial: {hist_err}")
            
            # Log action (audit)
            try:
                log_action(connection, 'tarjetas', entidad_id=tarjeta_id, entidad_tipo='tarjeta', accion='create', usuario=session.get('usuario') if session else 'Sistema', descripcion=f"Creada tarjeta uid={valores[0]}")
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
                if connection.__class__.__module__.startswith('sqlite3'):
                    placeholder = '?'
                cursor.execute(f"SELECT uid, nombre_completo, estado FROM tarjetas WHERE id = {placeholder}", (id,))
                tarjeta = cursor.fetchone()
                if not tarjeta:
                    return jsonify({'error': 'Tarjeta no encontrada'}), 404

                if hasattr(tarjeta, 'keys'):
                    tarjeta_dict = dict(tarjeta)
                    current_estado = tarjeta_dict.get('estado')
                    uid = tarjeta_dict.get('uid')
                    nombre_completo = tarjeta_dict.get('nombre_completo')
                else:
                    uid = tarjeta[0] if len(tarjeta) > 0 else ''
                    nombre_completo = tarjeta[1] if len(tarjeta) > 1 else ''
                    current_estado = tarjeta[2] if len(tarjeta) > 2 else None

                accion_text = 'alta' if estado == 1 else 'baja'
                descripcion = f"Tarjeta marcada como {accion_text}: {nombre_completo} ({uid})"
                if current_estado is not None and int(current_estado) == estado:
                    accion_text = 'sin cambio'
                    descripcion = f'No hubo cambio de estado para tarjeta: {nombre_completo} ({uid})'

                cursor.execute(f"UPDATE tarjetas SET estado = {placeholder} WHERE id = {placeholder}", (estado, id))
                connection.commit()

                try:
                    placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                    fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                    sql_hist = f"""
                        INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                        VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                    """
                    usuario = session.get('usuario') if session else 'Sistema'
                    cursor.execute(sql_hist, (
                        id,
                        str(uid or ''),
                        str(nombre_completo or ''),
                        accion_text,
                        usuario,
                        descripcion
                    ))
                    connection.commit()
                except Exception as hist_err:
                    print(f"[ERROR] No se registró cambio de estado en historial: {hist_err}")

                try:
                    log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion=accion_text, usuario=session.get('usuario') if session else 'Sistema', descripcion=f"Actualizado estado de tarjeta id={id} a {estado}")
                except Exception:
                    pass
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            connection.close()
        return jsonify({'success': True, 'accion': accion_text})

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cursor.execute(f"SELECT uid, nombre_completo, correo, pin, estado FROM tarjetas WHERE id = {placeholder}", (id,))
            tarjeta = cursor.fetchone()
            if not tarjeta:
                return jsonify({'error': 'Tarjeta no encontrada'}), 404

            if hasattr(tarjeta, 'keys'):
                tarjeta_dict = dict(tarjeta)
                current_uid = tarjeta_dict.get('uid')
                current_nombre_completo = tarjeta_dict.get('nombre_completo')
                current_correo = tarjeta_dict.get('correo')
                current_pin = tarjeta_dict.get('pin')
                current_estado = tarjeta_dict.get('estado')
            else:
                current_uid = tarjeta[0] if len(tarjeta) > 0 else None
                current_nombre_completo = tarjeta[1] if len(tarjeta) > 1 else None
                current_correo = tarjeta[2] if len(tarjeta) > 2 else None
                current_pin = tarjeta[3] if len(tarjeta) > 3 else None
                current_estado = tarjeta[4] if len(tarjeta) > 4 else None

            uid = data.get('uid', current_uid)
            nombre_completo = data.get('nombre_completo', current_nombre_completo)
            correo = data.get('correo', current_correo)

            pin_raw = data.get('pin')
            if pin_raw is None or pin_raw == '':
                pin = current_pin
            else:
                pin = str(pin_raw).strip()
                import re
                if not re.fullmatch(r"\d{8}", pin):
                    return jsonify({'error': 'invalid_pin', 'message': 'El PIN debe contener exactamente 8 dígitos'}), 400

            if 'estado' in data:
                estado = data.get('estado', current_estado)
                if estado not in (0, 1, '0', '1'):
                    estado = current_estado if current_estado in (0, 1, '0', '1') else 1
                estado = int(estado)
            else:
                estado = current_estado if current_estado in (0, 1, '0', '1') else 1
            sql = """
                UPDATE tarjetas SET uid=%s, nombre_completo=%s, correo=%s, pin=%s, estado=%s
                WHERE id=%s
            """
            if connection.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            try:
                cursor.execute(sql, [uid, nombre_completo, correo, pin, estado, id])
                connection.commit()
            except Exception as e:
                import sqlite3
                if isinstance(e, sqlite3.IntegrityError) or 'UNIQUE constraint failed' in str(e) or 'Duplicate entry' in str(e):
                    return jsonify({'error': 'duplicate_uid', 'message': 'El UID ya existe'}), 400
                raise

            # Sincronizar enrolar si el UID de la tarjeta cambió o si existen enrolamientos vinculados
            try:
                if uid is not None:
                    sync_sql = f"""
                        UPDATE enrolar
                        SET tarjeta_uid = {placeholder}, tarjeta_id = {placeholder}
                        WHERE tarjeta_id = {placeholder} OR (tarjeta_uid IS NOT NULL AND UPPER(TRIM(tarjeta_uid)) = UPPER(TRIM({placeholder})))
                    """
                    cursor.execute(sync_sql, (uid, id, id, current_uid or uid))
                    connection.commit()
            except Exception as sync_err:
                print(f"[ERROR] No se sincronizó enrolar tras editar tarjeta: {sync_err}")

            # Registrar cambios en historial
            try:
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                """
                usuario = session.get('usuario') if session else 'Sistema'
                cursor.execute(sql_hist, (
                    id,
                    str(uid or ''),
                    str(nombre_completo or ''),
                    'editada',
                    usuario,
                    f'Tarjeta editada: {nombre_completo or ""} ({uid or ""})'
                ))
                connection.commit()
            except Exception as hist_err:
                print(f"[ERROR] No se registró edición en historial: {hist_err}")

            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion='update', usuario=session.get('usuario') if session else 'Sistema', descripcion=f"Actualizada tarjeta id={id}")
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
                    uid = tarjeta['uid']
                    nombre_completo = tarjeta['nombre_completo']
                else:
                    uid = tarjeta[0] if len(tarjeta) > 0 else None
                    nombre_completo = tarjeta[1] if len(tarjeta) > 1 else None
            cursor.execute(f"UPDATE tarjetas SET estado = 0 WHERE id = {placeholder}", params)
            connection.commit()
            
            # Registrar en historial
            try:
                placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                sql_hist = f"""
                    INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                    VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                """
                usuario = session.get('usuario') if session else 'Sistema'
                cursor.execute(sql_hist, (
                    id,
                    uid,
                    nombre_completo,
                    'eliminada',
                    usuario,
                    f'Tarjeta eliminada: {nombre_completo} ({uid})'
                ))
                connection.commit()
            except Exception as hist_err:
                print(f"[ERROR] No se registró eliminación en historial: {hist_err}")
            
            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', accion='delete', usuario=session.get('usuario') if session else 'Sistema', descripcion=f"Eliminada tarjeta id={id}")
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
            cursor.execute(f"SELECT id, uid, nombre_completo, correo, estado FROM tarjetas WHERE id = {placeholder}", (id,))
            tarjeta = cursor.fetchone()
            if not tarjeta:
                return jsonify({'error': 'Tarjeta no encontrada'}), 404
            
            # Convertir a dict si es necesario
            if hasattr(tarjeta, 'keys'):
                tarjeta_dict = dict(tarjeta)
            else:
                # Si es tupla, mapear a dict manualmente
                tarjeta_dict = {
                    'id': tarjeta[0],
                    'uid': tarjeta[1] if len(tarjeta) > 1 else None,
                    'nombre_completo': tarjeta[2] if len(tarjeta) > 2 else None,
                    'correo': tarjeta[3] if len(tarjeta) > 3 else None,
                    'estado': tarjeta[4] if len(tarjeta) > 4 else None
                }
            
            uid = tarjeta_dict.get('uid', '')
            nombre_completo = tarjeta_dict.get('nombre_completo', '')
            usuario = session.get('usuario') if session else 'Sistema'
            
            # Procesar la acción
            if accion == 'eliminada':
                # Eliminar tarjeta
                cursor.execute(f"DELETE FROM tarjetas WHERE id = {placeholder}", (id,))
                connection.commit()
                # Registrar en historial - SIEMPRE registrar, incluso si hay error
                try:
                    placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                    fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                    sql_hist = f"""
                        INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                        VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                    """
                    cursor.execute(sql_hist, (id, uid, nombre_completo, 'eliminada', usuario, f'Tarjeta eliminada: {nombre_completo} ({uid})'))
                    connection.commit()
                except Exception as hist_err:
                    print(f"[ERROR] No se registró en historial (eliminada): {hist_err}")
            else:
                # Alta o Baja: actualizar estado
                new_estado = 1 if accion == 'alta' else 0
                current_estado = tarjeta_dict.get('estado')
                accion_text = accion
                descripcion = f'Tarjeta marcada como {accion}: {nombre_completo} ({uid})'
                if current_estado is not None and int(current_estado) == new_estado:
                    accion_text = 'sin cambio'
                    descripcion = f'No hubo cambio de estado para tarjeta: {nombre_completo} ({uid})'

                cursor.execute(
                    f"UPDATE tarjetas SET estado = {placeholder} WHERE id = {placeholder}",
                    (new_estado, id)
                )
                connection.commit()
                # Registrar en historial - SIEMPRE registrar, incluso si hay error
                try:
                    placeholder_hist = '?' if connection.__class__.__module__.startswith('sqlite3') else '%s'
                    fecha_hora_func = "datetime('now')" if connection.__class__.__module__.startswith('sqlite3') else 'NOW()'
                    sql_hist = f"""
                        INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion, fecha_hora)
                        VALUES ({placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {placeholder_hist}, {fecha_hora_func})
                    """
                    cursor.execute(sql_hist, (id, uid, nombre_completo, accion_text, usuario, descripcion))
                    connection.commit()
                except Exception as hist_err:
                    print(f"[ERROR] No se registró en historial ({accion_text}): {hist_err}")
            
            try:
                log_action(connection, 'tarjetas', entidad_id=id, entidad_tipo='tarjeta', 
                          accion=accion_text, usuario=usuario, descripcion=f"Acción {accion_text} en tarjeta id={id}")
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
