
from flask import Blueprint, request, jsonify, session
import re
from config.db import get_connection, log_action, EMAIL_ALLOWED_DOMAINS
import traceback

personas_api = Blueprint('personas_api', __name__)


# Helper para abrir conexión con manejo de errores
def try_get_connection():
    try:
        conn = get_connection()
        return conn, None
    except Exception as e:
        return None, str(e)


def ensure_persona_creation_history(connection):
    """Backfill historial_acciones for personas missing a create record."""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO historial_acciones (modulo, entidad_id, entidad_tipo, accion, usuario, descripcion)
            SELECT 'personas', p.id, 'persona', 'create', 'Sistema', 'Registro de persona existente sin historial de creación'
            FROM personas p
            WHERE NOT EXISTS (
                SELECT 1 FROM historial_acciones ha
                WHERE ha.entidad_id = p.id
                  AND ha.entidad_tipo = 'persona'
                  AND LOWER(ha.accion) IN ('create', 'crear')
            )
        """)
        connection.commit()
    except Exception:
        pass
    finally:
        try:
            cursor.close()
        except Exception:
            pass


# Listar personas
@personas_api.route('/api/personas', methods=['GET'])
def listar_personas():
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.ver', False):
        return jsonify({'error': 'forbidden', 'message': 'Acceso denegado'}), 403

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM personas WHERE estado = 1")
            # sqlite3.Row -> dict-like; pymysql returns dicts when using DictCursor
            rows = cursor.fetchall()
            # Normalize sqlite rows to dicts
            if rows and hasattr(rows[0], 'keys'):
                personas = [dict(r) for r in rows]
            else:
                personas = rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(personas)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        connection.close()

# Registrar persona
@personas_api.route('/api/personas', methods=['POST'])
def registrar_persona():
    # --- Verificar permisos de creación ---
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.crear', False):
        return jsonify({
            'success': False,
            'message': 'Acceso denegado: Tu rol no tiene permisos para crear registros.'
        }), 403
    
    data = request.get_json()
    # --- Validar correo antes de proceder ---
    correo = (data.get('correo') or '').strip()
    if correo:
        # formato básico de email
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if not email_re.match(correo):
            return jsonify({'success': False, 'error': 'Formato de correo inválido.', 'error_code': 'invalid_email'}), 400
        # si hay dominios permitidos configurados, comprobar que el dominio esté en la lista
        if EMAIL_ALLOWED_DOMAINS:
            domain = correo.split('@')[-1].lower()
            if domain not in EMAIL_ALLOWED_DOMAINS:
                return jsonify({'success': False, 'error': f'El correo debe pertenecer a uno de los dominios permitidos: {",".join(EMAIL_ALLOWED_DOMAINS)}', 'error_code': 'email_domain_not_allowed'}), 400
    else:
        return jsonify({'success': False, 'error': 'El campo correo es requerido.', 'error_code': 'missing_email'}), 400
    campos = [
        'nombre_completo', 'fecha_nacimiento', 'correo', 'telefono_personal',
        'documento_identidad', 'sexo', 'tipo_sangre', 'rol', 'estado', 'persona_emergencia', 'telefono_emergencia'
    ]
    estado_value = data.get('estado', 1)
    if estado_value not in (0, 1, '0', '1'):
        estado_value = 1
    else:
        estado_value = int(estado_value)
    valores = [
        data.get('nombre_completo'),
        data.get('fecha_nacimiento'),
        data.get('correo'),
        data.get('telefono_personal'),
        data.get('documento_identidad'),
        data.get('sexo'),
        data.get('tipo_sangre'),
        data.get('rol'),
        estado_value,
        data.get('persona_emergencia'),
        data.get('telefono_emergencia'),
    ]
    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            # If the client provided an id or documento_identidad that already exists,
            # treat this POST as an update to avoid creating duplicates (backwards compatibility
            # with older frontend builds that use POST for edit).
            placeholder = '%s'
            params = ()
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'

            existing_id = None
            if data.get('id'):
                params = (data.get('id'),)
                cursor.execute(f"SELECT id FROM personas WHERE id = {placeholder}", params)
                row = cursor.fetchone()
                if row:
                    existing_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)

            if existing_id is None and data.get('documento_identidad'):
                params = (data.get('documento_identidad'),)
                cursor.execute(f"SELECT id FROM personas WHERE documento_identidad = {placeholder} LIMIT 1", params)
                row = cursor.fetchone()
                if row:
                    existing_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)

            if existing_id:
                # perform update
                sql = """
                    UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s,
                    documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, estado=%s, persona_emergencia=%s, telefono_emergencia=%s
                    WHERE id=%s
                """
                if connection.__class__.__module__.startswith('sqlite3'):
                    sql = sql.replace('%s', '?')
                cursor.execute(sql, valores + [existing_id])
                connection.commit()
                try:
                    log_action(connection, 'personas', entidad_id=existing_id, entidad_tipo='persona', accion='update', usuario=session.get('usuario') if session else None, descripcion=f"Actualizada persona id={existing_id}")
                except Exception:
                    pass
                return jsonify({'success': True})

            # Otherwise insert as new
            sql = """
                INSERT INTO personas (nombre_completo, fecha_nacimiento, correo, telefono_personal, documento_identidad, sexo, tipo_sangre, rol, estado, persona_emergencia, telefono_emergencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # sqlite uses ? placeholders; pymysql uses %s. Detect and adapt.
            if connection.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            cursor.execute(sql, valores)
            connection.commit()
            try:
                log_action(connection, 'personas', entidad_id=cursor.lastrowid if hasattr(cursor, 'lastrowid') else None, entidad_tipo='persona', accion='create', usuario=session.get('usuario') if session else None, descripcion=f"Creada persona {valores[0]}")
            except Exception:
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'insert_failed'}), 500
    finally:
        connection.close()

# Obtener persona por ID
@personas_api.route('/api/personas/<int:id>', methods=['GET'])
def obtener_persona(id):
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.ver', False):
        return jsonify({'error': 'forbidden', 'message': 'Acceso denegado'}), 403

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (id,)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cursor.execute(f"SELECT * FROM personas WHERE id = {placeholder}", params)
            persona = cursor.fetchone()
            if persona and hasattr(persona, 'keys'):
                persona = dict(persona)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        if not persona:
            return jsonify({'error': 'No encontrada'}), 404
        return jsonify(persona)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        connection.close()

# Editar persona
@personas_api.route('/api/personas/<int:id>', methods=['PUT'])
def editar_persona(id):
    # --- Verificar permisos de edición ---
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.editar', False):
        return jsonify({
            'success': False,
            'message': 'Acceso denegado: Tu rol no tiene permisos para editar registros.'
        }), 403
    
    data = request.get_json()
    # --- Validar correo solo si se proporcionó ---
    correo = (data.get('correo') or '').strip()
    if correo:
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if not email_re.match(correo):
            return jsonify({'success': False, 'error': 'Formato de correo inválido.', 'error_code': 'invalid_email'}), 400
        if EMAIL_ALLOWED_DOMAINS:
            domain = correo.split('@')[-1].lower()
            if domain not in EMAIL_ALLOWED_DOMAINS:
                return jsonify({'success': False, 'error': f'El correo debe pertenecer a uno de los dominios permitidos: {",".join(EMAIL_ALLOWED_DOMAINS)}', 'error_code': 'email_domain_not_allowed'}), 400

    # Include 'estado' so SQL placeholders align with provided values
    campos = [
        'nombre_completo', 'fecha_nacimiento', 'correo', 'telefono_personal',
        'documento_identidad', 'sexo', 'tipo_sangre', 'rol', 'estado', 'persona_emergencia', 'telefono_emergencia'
    ]
    valores = [data.get(campo) for campo in campos]
    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (id,)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            if data.get('estado') not in (0, 1, '0', '1'):
                cursor.execute(f"SELECT estado FROM personas WHERE id = {placeholder}", params)
                existing = cursor.fetchone()
                if existing:
                    valores[8] = existing[0] if isinstance(existing, (list, tuple)) else (existing.get('estado') if hasattr(existing, 'get') else existing)
                else:
                    valores[8] = 1
            else:
                valores[8] = int(data.get('estado'))

            sql = """
                UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s,
                documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, estado=%s, persona_emergencia=%s, telefono_emergencia=%s
                WHERE id=%s
            """
            if connection.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            cursor.execute(sql, valores + [id])
            connection.commit()
            try:
                log_action(connection, 'personas', entidad_id=id, entidad_tipo='persona', accion='update', usuario=session.get('usuario') if session else None, descripcion=f"Actualizada persona id={id}")
            except Exception:
                pass
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


# Actualizar solo el estado de una persona
@personas_api.route('/api/personas/<int:id>/estado', methods=['PUT'])
def actualizar_estado_persona(id):
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.editar', False):
        return jsonify({'error': 'forbidden', 'message': 'Acceso denegado'}), 403

    data = request.get_json() or {}
    estado = data.get('estado')
    if estado not in (0, 1, '0', '1'):
        return jsonify({'success': False, 'error': 'Estado inválido. Debe ser 0 o 1.'}), 400
    estado = int(estado)

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            params = (estado, id)
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            sql = f"UPDATE personas SET estado = {placeholder} WHERE id = {placeholder}"
            print(f"[DEBUG] Actualizando estado={estado} para persona id={id}")
            print(f"[DEBUG] SQL: {sql}, params: {params}")
            cursor.execute(sql, params)
            print(f"[DEBUG] cursor.execute completado, ahora ejecutando commit...")
            connection.commit()
            print(f"[DEBUG] ✓ COMMIT EXITOSO para estado de persona {id}")
            try:
                accion = 'activate' if estado == 1 else 'deactivate'
                log_action(connection, 'personas', entidad_id=id, entidad_tipo='persona', accion=accion, usuario=session.get('usuario') if session else None, descripcion=f"{'Activada' if estado == 1 else 'Inactivada'} persona id={id}")
            except Exception as log_err:
                print(f"[WARNING] Error en log_action: {log_err}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERROR] UPDATE estado failed: {e}")
        traceback.print_exc()
        return jsonify({'error': 'update_failed', 'message': str(e)}), 500
    finally:
        connection.close()


# Eliminar persona por ID o correo (API)
@personas_api.route('/api/personas/<int:id>', methods=['DELETE'])
def eliminar_persona_api(id):
    # --- Verificar permisos de eliminación ---
    permissions = session.get('permissions', {})
    if not permissions.get('administracion.eliminar', False):
        return jsonify({
            'success': False,
            'message': 'Acceso denegado: Tu rol no tiene permisos para eliminar registros.'
        }), 403
    
    correo_query = (request.args.get('correo') or '').strip()
    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'

            if correo_query:
                # Buscar persona por correo para eliminar en cascada
                if connection.__class__.__module__.startswith('sqlite3'):
                    cursor.execute("SELECT id, correo FROM personas WHERE LOWER(correo) = LOWER(?) LIMIT 1", (correo_query,))
                else:
                    cursor.execute("SELECT id, correo FROM personas WHERE LOWER(correo) = LOWER(%s) LIMIT 1", (correo_query,))
                persona_row = cursor.fetchone()
                if not persona_row:
                    return jsonify({'success': False, 'message': 'Persona no encontrada por correo.'}), 404
                persona_id = persona_row['id'] if hasattr(persona_row, 'keys') else persona_row[0]
                persona_correo = persona_row['correo'] if hasattr(persona_row, 'keys') else persona_row[1]
            else:
                persona_id = id
                # obtener correo para limpiar usuarios vinculados por correo también
                if connection.__class__.__module__.startswith('sqlite3'):
                    cursor.execute("SELECT correo FROM personas WHERE id = ? LIMIT 1", (persona_id,))
                else:
                    cursor.execute("SELECT correo FROM personas WHERE id = %s LIMIT 1", (persona_id,))
                persona_row = cursor.fetchone()
                if not persona_row:
                    return jsonify({'success': False, 'message': 'Persona no encontrada.'}), 404
                persona_correo = persona_row['correo'] if hasattr(persona_row, 'keys') else persona_row[0]

            # Borrado lógico: marcar como inactivo la persona y sus usuarios vinculados.
            # IMPORTANTE: usar parametrized queries sin f-strings para evitar problemas de sustitución
            if connection.__class__.__module__.startswith('sqlite3'):
                # SQLite: ? placeholder
                print(f"[DEBUG] Marcando persona {persona_id} como inactivo (SQLite)")
                cursor.execute("UPDATE personas SET estado = 0 WHERE id = ?", (persona_id,))
                print(f"[DEBUG] Actualizados usuarios vinculados a {persona_id}")
                cursor.execute(
                    "UPDATE usuario_sistema SET estado = 0 WHERE persona_id = ? OR LOWER(nombre_usuario) = LOWER(?)",
                    (persona_id, persona_correo)
                )
            else:
                # MySQL: %s placeholder
                print(f"[DEBUG] Marcando persona {persona_id} como inactivo (MySQL)")
                cursor.execute("UPDATE personas SET estado = 0 WHERE id = %s", (persona_id,))
                print(f"[DEBUG] Actualizados usuarios vinculados a {persona_id}")
                cursor.execute(
                    "UPDATE usuario_sistema SET estado = 0 WHERE persona_id = %s OR LOWER(nombre_usuario) = LOWER(%s)",
                    (persona_id, persona_correo)
                )
            print(f"[DEBUG] Ejecutando connection.commit() para persona {persona_id}...")
            connection.commit()
            print(f"[DEBUG] ✓ COMMIT EXITOSO para persona {persona_id}")
            try:
                log_action(
                    connection,
                    'personas',
                    entidad_id=persona_id,
                    entidad_tipo='persona',
                    accion='delete',
                    usuario=session.get('usuario') if session else None,
                    descripcion=f"Eliminada persona id={persona_id} y desactivados usuarios vinculados"
                )
            except Exception as log_err:
                print(f"[WARNING] Error en log_action: {log_err}")
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERROR] Delete persona failed: {e}")
        return jsonify({'error': 'delete_failed', 'message': str(e)}), 500
    finally:
        connection.close()


# Buscar personas y adjuntar tarjeta asociada (uid, pin) si existe
# Returns ALL matching personas (allows handling duplicates in frontend with dropdown)
@personas_api.route('/api/personas/search_with_tarjeta', methods=['GET'])
def search_personas_with_tarjeta():
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify([])
    conn, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cur = conn.cursor()
        try:
            placeholder = '%s'
            if conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            like = f"%{q}%"
            # Left join tarjetas to include uid/pin when available (match by correo or nombre_completo)
            # Order by nombre_completo to group similar names, then by id
            sql = (
                "SELECT personas.*, tarjetas.uid AS tarjeta_uid, tarjetas.pin AS tarjeta_pin "
                "FROM personas LEFT JOIN tarjetas ON (personas.correo = tarjetas.correo OR personas.nombre_completo = tarjetas.nombre_completo) "
                f"WHERE personas.estado = 1 AND (personas.nombre_completo LIKE {placeholder} OR personas.correo LIKE {placeholder}) "
                "ORDER BY personas.nombre_completo ASC, personas.id ASC"
            )
            params = (like, like)
            cur.execute(sql, params)
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                results = [dict(r) for r in rows]
            else:
                results = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(results)
    finally:
        conn.close()


# Reporte: Historial de acciones en personas
# Retorna todas las acciones realizadas en personas
@personas_api.route('/api/reportes/personas-registradas-sin-tarjeta', methods=['GET'])
def reporte_personas_sin_tarjeta():
    """
    Retorna un reporte de acciones en personas.
    
    Lógica:
    1. Une historial_acciones con personas para obtener todas las acciones.
    2. Aplica filtros opcionales de búsqueda, responsable y fecha.
    
    Retorna: id, documento_identidad, nombre_completo, fecha_hora, usuario, accion
    """
    search = (request.args.get('buscar') or '').strip()
    responsable = (request.args.get('responsable') or '').strip()
    fecha_desde = (request.args.get('fecha_desde') or '').strip()

    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    
    try:
        cursor = connection.cursor()
        try:
            placeholder = '%s'
            if connection.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'

            sql = """
            SELECT
                ha.id,
                p.documento_identidad,
                p.nombre_completo,
                ha.fecha_hora,
                ha.usuario,
                ha.accion
            FROM historial_acciones ha
            JOIN personas p ON ha.entidad_id = p.id
            WHERE ha.entidad_tipo = 'persona'
            """

            where_clauses = []
            params = []

            if search:
                where_clauses.append(f"(p.documento_identidad LIKE {placeholder} OR p.nombre_completo LIKE {placeholder})")
                like_value = f"%{search}%"
                params.extend([like_value, like_value])

            if responsable:
                where_clauses.append(f"ha.usuario LIKE {placeholder}")
                params.append(f"%{responsable}%")

            if fecha_desde:
                if connection.__class__.__module__.startswith('sqlite3'):
                    where_clauses.append(f"date(ha.fecha_hora) >= date({placeholder})")
                else:
                    where_clauses.append(f"date(ha.fecha_hora) >= {placeholder}")
                params.append(fecha_desde)

            if where_clauses:
                sql += "\nAND " + " AND ".join(where_clauses)

            sql += "\nORDER BY ha.fecha_hora DESC, p.nombre_completo ASC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []

            # Normalizar resultados a dicts, tanto si el cursor entrega dict-like rows como tuplas.
            if rows and hasattr(rows[0], 'keys'):
                resultados = [dict(r) for r in rows]
            else:
                resultados = [dict(zip(column_names, row)) for row in rows]

            return jsonify(resultados)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed', 'message': str(traceback.format_exc())}), 500
    finally:
        connection.close()
