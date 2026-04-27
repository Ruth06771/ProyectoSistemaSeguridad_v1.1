
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


# Listar personas
@personas_api.route('/api/personas', methods=['GET'])
def listar_personas():
    connection, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM personas")
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
    valores = [data.get(campo) for campo in campos]
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
                    documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s
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


# Eliminar persona por ID (API)
@personas_api.route('/api/personas/<int:id>', methods=['DELETE'])
def eliminar_persona_api(id):
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
            cursor.execute(f"DELETE FROM personas WHERE id = {placeholder}", params)
            connection.commit()
            try:
                log_action(connection, 'personas', entidad_id=id, entidad_tipo='persona', accion='delete', usuario=session.get('usuario') if session else None, descripcion=f"Eliminada persona id={id}")
            except Exception:
                pass
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        return jsonify({'error': 'delete_failed'}), 500
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
                f"WHERE personas.nombre_completo LIKE {placeholder} OR personas.correo LIKE {placeholder} "
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
