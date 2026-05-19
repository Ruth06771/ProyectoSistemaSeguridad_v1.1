from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import traceback
import sqlite3

enrolar_api = Blueprint('enrolar_api', __name__)


def _sql_placeholder(conn):
    return '?' if conn.__class__.__module__.startswith('sqlite3') else '%s'


def _apply_placeholder(sql, conn):
    return sql.replace('%s', '?') if conn.__class__.__module__.startswith('sqlite3') else sql


def _row_to_dict(cursor, row):
    if row is None:
        return None
    if hasattr(row, 'keys'):
        return dict(row)
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return {cols[i]: row[i] for i in range(len(cols))}


@enrolar_api.route('/api/perfil_acceso_lab', methods=['GET'])
def listar_perfil_acceso_lab():
    """Devuelve una lista de perfiles de acceso a laboratorios (id, nombre, estado)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            placeholder = '%s'
            if conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cur.execute("SELECT id, nombre, estado FROM perfil_acceso_lab ORDER BY nombre ASC")
            rows = cur.fetchall()
            results = []
            if rows:
                # sqlite Row objects may have 'keys'
                if hasattr(rows[0], 'keys'):
                    results = [dict(r) for r in rows]
                else:
                    results = [{'id': r[0], 'nombre': r[1], 'estado': r[2]} for r in rows]
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(results)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'query_failed'}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass 


@enrolar_api.route('/api/enrolar', methods=['POST'])
def enrolar_persona_tarjeta():
    """Endpoint que recibe un objeto con 'persona', 'tarjeta' y opcional 'perfil'.
    Inserta las tres entidades en una misma transacción (si la DB lo soporta)
    y retorna success/failed.
    """
    data = request.get_json() or {}
    persona = data.get('persona', {})
    tarjeta = data.get('tarjeta', {})
    perfil = data.get('perfil')  # perfil puede ser None o dict

    conn = get_connection()
    try:
        # Ensure perfiles table exists (in sqlite fallback it's safe)
        cur = conn.cursor()
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS perfiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id INTEGER,
                    nombre TEXT,
                    datos TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            try:
                cur.close()
            except Exception:
                pass

        cur = conn.cursor()
        try:
            # Insert or update persona: if frontend provided an id or documento_identidad
            # that already exists, update that persona instead of creating a duplicate.
            campos = [
                'nombre_completo', 'fecha_nacimiento', 'correo', 'telefono_personal',
                'documento_identidad', 'sexo', 'tipo_sangre', 'rol', 'persona_emergencia', 'telefono_emergencia', 'emergencia_relacion', 'emergencia_direccion'
            ]
            valores = [persona.get(c) for c in campos]

            persona_id = None
            updated_existing = False

            # Helper: placeholder style
            placeholder = '%s'
            if conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'

            # If an ID was provided, try to update that persona
            if persona.get('id'):
                try:
                    # check exists
                    cur.execute(f"SELECT id FROM personas WHERE id = {placeholder}", (persona.get('id'),))
                    row = cur.fetchone()
                    if row:
                        # perform update
                        update_sql = ("UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s, "
                                      "documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s, emergencia_relacion=%s, emergencia_direccion=%s "
                                      "WHERE id=%s")
                        if conn.__class__.__module__.startswith('sqlite3'):
                            update_sql = update_sql.replace('%s', '?')
                        cur.execute(update_sql, valores + [persona.get('id')])
                        persona_id = persona.get('id')
                        updated_existing = True
                except Exception:
                    # ignore and fall back to insert
                    pass

            # If not updated by id, try documento_identidad
            if not updated_existing and persona.get('documento_identidad'):
                try:
                    cur.execute(f"SELECT id FROM personas WHERE documento_identidad = {placeholder} LIMIT 1", (persona.get('documento_identidad'),))
                    row = cur.fetchone()
                    if row:
                        existing_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)
                        update_sql = ("UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s, "
                                      "documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s, emergencia_relacion=%s, emergencia_direccion=%s "
                                      "WHERE id=%s")
                        if conn.__class__.__module__.startswith('sqlite3'):
                            update_sql = update_sql.replace('%s', '?')
                        cur.execute(update_sql, valores + [existing_id])
                        persona_id = existing_id
                        updated_existing = True
                except Exception:
                    pass

            # Fallback: try match by correo
            if not updated_existing and persona.get('correo'):
                try:
                    cur.execute(f"SELECT id FROM personas WHERE correo = {placeholder} LIMIT 1", (persona.get('correo'),))
                    row = cur.fetchone()
                    if row:
                        existing_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)
                        update_sql = ("UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s, "
                                      "documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s, emergencia_relacion=%s, emergencia_direccion=%s "
                                      "WHERE id=%s")
                        if conn.__class__.__module__.startswith('sqlite3'):
                            update_sql = update_sql.replace('%s', '?')
                        cur.execute(update_sql, valores + [existing_id])
                        persona_id = existing_id
                        updated_existing = True
                except Exception:
                    pass

            # Fallback: try match by exact nombre_completo (last resort)
            if not updated_existing and persona.get('nombre_completo'):
                try:
                    cur.execute(f"SELECT id FROM personas WHERE nombre_completo = {placeholder} LIMIT 1", (persona.get('nombre_completo'),))
                    row = cur.fetchone()
                    if row:
                        existing_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)
                        update_sql = ("UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s, "
                                      "documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s, emergencia_relacion=%s, emergencia_direccion=%s "
                                      "WHERE id=%s")
                        if conn.__class__.__module__.startswith('sqlite3'):
                            update_sql = update_sql.replace('%s', '?')
                        cur.execute(update_sql, valores + [existing_id])
                        persona_id = existing_id
                        updated_existing = True
                except Exception:
                    pass

            # If still not updated, insert new persona
            if not updated_existing:
                sql = """
                    INSERT INTO personas (nombre_completo, fecha_nacimiento, correo, telefono_personal, documento_identidad, sexo, tipo_sangre, rol, persona_emergencia, telefono_emergencia, emergencia_relacion, emergencia_direccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                if conn.__class__.__module__.startswith('sqlite3'):
                    sql = sql.replace('%s', '?')
                cur.execute(sql, valores)
                persona_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None

            # Handle tarjeta: if uid exists, use existing; otherwise insert new (including pin if provided)
            tarjeta_id = None
            existing_tarjeta = None
            if tarjeta.get('uid'):
                try:
                    cur.execute(f"SELECT id, uid, nombre_completo, correo, pin FROM tarjetas WHERE uid = {placeholder} LIMIT 1", (tarjeta.get('uid'),))
                    existing_tarjeta = cur.fetchone()
                    if existing_tarjeta:
                        # sqlite Row or tuple
                        if hasattr(existing_tarjeta, 'keys'):
                            tarjeta_id = existing_tarjeta['id']
                        else:
                            tarjeta_id = existing_tarjeta[0]
                except Exception:
                    existing_tarjeta = None

            if not tarjeta_id:
                # insert new tarjeta; accept pin when provided
                t_campos = ['uid', 'nombre_completo', 'correo', 'pin']
                t_vals = [tarjeta.get(c) for c in t_campos]
                # server-side validation for PIN if provided
                pin_val = (tarjeta.get('pin') or '')
                if pin_val is not None and str(pin_val).strip() != '':
                    import re
                    if not re.fullmatch(r"\d{8}", str(pin_val).strip()):
                        conn.rollback()
                        return jsonify({'error': 'invalid_pin', 'message': 'El PIN debe contener exactamente 8 dígitos'}), 400
                    t_vals[3] = str(pin_val).strip()
                else:
                    t_vals[3] = None

                sql_t = "INSERT INTO tarjetas (uid, nombre_completo, correo, pin) VALUES (%s, %s, %s, %s)"
                if conn.__class__.__module__.startswith('sqlite3'):
                    sql_t = sql_t.replace('%s', '?')
                try:
                    cur.execute(sql_t, t_vals)
                    tarjeta_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
                except sqlite3.IntegrityError as ie:
                    # likely duplicate UID inserted concurrently — try to lookup the existing tarjeta instead of failing
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    try:
                        cur.execute(f"SELECT id FROM tarjetas WHERE uid = {placeholder} LIMIT 1", (tarjeta.get('uid'),))
                        row = cur.fetchone()
                        if row:
                            tarjeta_id = row[0] if isinstance(row, (list, tuple)) else (row.get('id') if hasattr(row, 'get') else None)
                        else:
                            return jsonify({'error': 'duplicate_uid', 'message': 'El UID de la tarjeta ya existe pero no se pudo recuperar el registro'}), 400
                    except Exception:
                        return jsonify({'error': 'duplicate_uid', 'message': 'El UID de la tarjeta ya existe y no se pudo recuperar'}), 400

            # Insert enrolar record linking persona and tarjeta (uses tarjeta_uid) and track action state
            try:
                action_value = 'activo'
                perfil_access_id = perfil.get('perfil_acceso_lab_id') if perfil and isinstance(perfil, dict) else None
                enrolar_sql = "INSERT INTO enrolar (persona_id, tarjeta_uid, tarjeta_id, perfil_acceso_lab_id, accion) VALUES (%s, %s, %s, %s, %s)"
                enrolar_vals = (persona_id, tarjeta.get('uid'), tarjeta_id, perfil_access_id, action_value)
                if conn.__class__.__module__.startswith('sqlite3'):
                    enrolar_sql = enrolar_sql.replace('%s', '?')
                cur.execute(enrolar_sql, enrolar_vals)
                enrolar_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
            except Exception:
                # non-critical, continue but set enrolar_id to None
                enrolar_id = None

            # Insert historial_tarjetas entry for the enrollment action
            try:
                historial_sql = "INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion) VALUES (%s, %s, %s, %s, %s, %s)"
                historial_vals = (
                    tarjeta_id,
                    tarjeta.get('uid'),
                    persona.get('nombre_completo') or tarjeta.get('nombre_completo'),
                    'alta',
                    session.get('usuario') if session else None,
                    f"Enrolada persona_id={persona_id} con tarjeta uid={tarjeta.get('uid')}"
                )
                if conn.__class__.__module__.startswith('sqlite3'):
                    historial_sql = historial_sql.replace('%s', '?')
                cur.execute(historial_sql, historial_vals)
            except Exception:
                pass

            # Insert perfil (opcional)
            perfil_id = None
            if perfil:
                sql_p = "INSERT INTO perfiles (persona_id, nombre, datos) VALUES (%s, %s, %s)"
                p_vals = (persona_id, perfil.get('nombre'), perfil.get('datos'))
                if conn.__class__.__module__.startswith('sqlite3'):
                    sql_p = sql_p.replace('%s', '?')
                cur.execute(sql_p, p_vals)
                perfil_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None

            conn.commit()

            # Record enrollment history
            try:
                hist_sql = "INSERT INTO historial_enrolamiento (enrolar_id, persona_id, nombre_persona, perfil, tarjeta_uid, tarjeta_pin, estado, responsable, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                if conn.__class__.__module__.startswith('sqlite3'):
                    hist_sql = hist_sql.replace('%s', '?')
                hist_vals = (
                    enrolar_id,
                    persona_id,
                    persona.get('nombre_completo') if persona else None,
                    (perfil.get('nombre') if isinstance(perfil, dict) else perfil) if perfil else None,
                    tarjeta.get('uid') if tarjeta else None,
                    (tarjeta.get('pin') if tarjeta else None),
                    action_value,
                    session.get('usuario') if session else None,
                    f"Enrolamiento {action_value} persona_id={persona_id} tarjeta_uid={tarjeta.get('uid') if tarjeta else None}"
                )
                cur.execute(hist_sql, hist_vals)
            except Exception:
                pass

            # Log actions
            try:
                log_action(conn, 'personas', entidad_id=persona_id, entidad_tipo='persona', accion='create', usuario=session.get('usuario') if session else None, descripcion=f'Enrolada persona {persona.get("nombre_completo")}')
            except Exception:
                pass
            try:
                log_action(conn, 'tarjetas', entidad_id=tarjeta_id, entidad_tipo='tarjeta', accion='create', usuario=session.get('usuario') if session else None, descripcion=f'Enrolada tarjeta uid={tarjeta.get("uid")}')
            except Exception:
                pass
            if perfil_id:
                try:
                    log_action(conn, 'perfiles', entidad_id=perfil_id, entidad_tipo='perfil', accion='create', usuario=session.get('usuario') if session else None, descripcion=f'Creado perfil id={perfil_id} para persona_id={persona_id}')
                except Exception:
                    pass

        finally:
            try:
                cur.close()
            except Exception:
                pass

        return jsonify({'success': True, 'persona_id': persona_id, 'tarjeta_id': tarjeta_id, 'perfil_id': perfil_id, 'enrolar_id': enrolar_id})
    except Exception:
        traceback.print_exc()
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({'error': 'enrol_failed'}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@enrolar_api.route('/api/enrolar', methods=['GET'])
def listar_enrolamientos():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA table_info(enrolar)")
            cols = [c[1] for c in cursor.fetchall()]
            date_field = 'fecha_de_registro' if 'fecha_de_registro' in cols else 'fecha_registro'
            sql = f'''
            SELECT
                e.id AS enrolar_id,
                e.persona_id,
                e.tarjeta_id,
                e.tarjeta_uid,
                e.perfil_acceso_lab_id,
                e.estado AS enrolar_estado,
                e.accion AS enrolar_accion,
                e.{date_field} AS fecha_registro,
                p.nombre_completo AS persona_nombre,
                p.correo AS persona_correo,
                p.documento_identidad AS persona_documento,
                p.tipo_sangre AS persona_tipo_sangre,
                p.estado AS persona_estado,
                t.uid AS tarjeta_uid_real,
                t.pin AS tarjeta_pin,
                t.estado AS tarjeta_estado,
                pa.nombre AS perfil_nombre,
                pf.nombre AS perfil_personal_nombre,
                e.perfil_acceso_lab_id AS perfil_raw
            FROM enrolar e
            LEFT JOIN personas p ON p.id = e.persona_id
            LEFT JOIN tarjetas t ON t.id = e.tarjeta_id OR (e.tarjeta_uid IS NOT NULL AND t.uid = e.tarjeta_uid)
            LEFT JOIN perfil_acceso_lab pa ON pa.id = e.perfil_acceso_lab_id
            LEFT JOIN (
                SELECT persona_id, nombre
                FROM perfiles
                WHERE id IN (SELECT MAX(id) FROM perfiles GROUP BY persona_id)
            ) pf ON pf.persona_id = p.id
            ORDER BY e.{date_field} DESC
            '''
            cursor.execute(sql)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                row = _row_to_dict(cursor, r)
                results.append({
                    'id': row.get('enrolar_id'),
                    'persona_id': row.get('persona_id'),
                    'tarjeta_id': row.get('tarjeta_id'),
                    'tarjeta_uid': row.get('tarjeta_uid_real') or row.get('tarjeta_uid'),
                    'perfil_id': row.get('perfil_acceso_lab_id'),
                    'perfil': row.get('perfil_nombre') or row.get('perfil_personal_nombre') or (row.get('perfil_raw') if row.get('perfil_raw') is not None else None),
                    'accion': row.get('enrolar_accion'),
                    'estado': row.get('enrolar_estado'),
                    'fecha_de_registro': row.get('fecha_registro'),
                    'nombre_completo': row.get('persona_nombre'),
                    'correo': row.get('persona_correo'),
                    'documento_identidad': row.get('persona_documento'),
                    'tipo_sangre': row.get('persona_tipo_sangre'),
                    'persona_estado': row.get('persona_estado'),
                    'pin': row.get('tarjeta_pin'),
                    'tarjeta_estado': row.get('tarjeta_estado')
                })
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(results)
    finally:
        connection.close()


@enrolar_api.route('/api/enrolar/<int:id>', methods=['PUT'])
def actualizar_enrolar(id):
    data = request.get_json() or {}
    persona = data.get('persona', {})
    tarjeta = data.get('tarjeta', {})
    perfil = data.get('perfil')
    estado = data.get('estado')
    accion = data.get('accion')

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = _sql_placeholder(connection)
            cursor.execute(_apply_placeholder('SELECT persona_id, tarjeta_id, tarjeta_uid FROM enrolar WHERE id = %s', connection), (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'not_found'}), 404

            persona_id = row[0] if isinstance(row, (list, tuple)) else row.get('persona_id')
            tarjeta_id = row[1] if isinstance(row, (list, tuple)) else row.get('tarjeta_id')
            tarjeta_uid = row[2] if isinstance(row, (list, tuple)) else row.get('tarjeta_uid')

            if persona_id and persona:
                campos = [
                    'nombre_completo', 'fecha_nacimiento', 'correo', 'telefono_personal',
                    'documento_identidad', 'sexo', 'tipo_sangre', 'rol', 'persona_emergencia', 'telefono_emergencia', 'emergencia_relacion', 'emergencia_direccion'
                ]
                valores = [persona.get(c) for c in campos] + [persona_id]
                sql = '''
                    UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s,
                    documento_identidad=%s, sexo=%s, tipo_sangre=%s, rol=%s, persona_emergencia=%s, telefono_emergencia=%s,
                    emergencia_relacion=%s, emergencia_direccion=%s WHERE id=%s
                '''
                cursor.execute(_apply_placeholder(sql, connection), valores)

            # Update or insert tarjeta if needed
            if tarjeta:
                if tarjeta_id:
                    update_sql = '''
                        UPDATE tarjetas SET uid=%s, nombre_completo=%s, correo=%s, pin=%s WHERE id=%s
                    '''
                    t_vals = [tarjeta.get('uid'), tarjeta.get('nombre_completo'), tarjeta.get('correo'), tarjeta.get('pin'), tarjeta_id]
                    cursor.execute(_apply_placeholder(update_sql, connection), t_vals)
                elif tarjeta_uid:
                    update_sql = '''
                        UPDATE tarjetas SET uid=%s, nombre_completo=%s, correo=%s, pin=%s WHERE uid=%s
                    '''
                    t_vals = [tarjeta.get('uid'), tarjeta.get('nombre_completo'), tarjeta.get('correo'), tarjeta.get('pin'), tarjeta_uid]
                    cursor.execute(_apply_placeholder(update_sql, connection), t_vals)

            update_fields = []
            update_values = []
            if perfil is not None:
                update_fields.append('perfil_acceso_lab_id = %s')
                update_values.append(perfil.get('perfil_acceso_lab_id') if isinstance(perfil, dict) else perfil)
            if estado is not None:
                try:
                    estado_int = int(estado)
                except Exception:
                    estado_int = 1
                update_fields.append('estado = %s')
                update_values.append(estado_int)
            if tarjeta.get('uid'):
                update_fields.append('tarjeta_uid = %s')
                update_values.append(tarjeta.get('uid'))

            if accion is not None:
                update_fields.append('accion = %s')
                update_values.append(accion)

            if update_fields:
                sql = f"UPDATE enrolar SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(_apply_placeholder(sql, connection), update_values + [id])

            connection.commit()
            # Record update in enrollment history
            try:
                hist_sql = "INSERT INTO historial_enrolamiento (enrolar_id, persona_id, nombre_persona, perfil, tarjeta_uid, tarjeta_pin, estado, responsable, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                if connection.__class__.__module__.startswith('sqlite3'):
                    hist_sql = hist_sql.replace('%s', '?')
                perfil_name = None
                if perfil:
                    perfil_name = perfil.get('nombre') if isinstance(perfil, dict) else perfil
                hist_vals = (
                    id,
                    persona_id,
                    (persona.get('nombre_completo') if persona else None),
                    perfil_name,
                    (tarjeta.get('uid') if tarjeta else None),
                    (tarjeta.get('pin') if tarjeta else None),
                    (accion if accion is not None else ('editado' if 'editado' in (update_values or []) else None)),
                    session.get('usuario') if session else None,
                    f"Enrolamiento actualizado id={id} accion={accion}"
                )
                cursor.execute(_apply_placeholder(hist_sql, connection), hist_vals)
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


@enrolar_api.route('/api/enrolar/<int:id>', methods=['DELETE'])
def eliminar_enrolar(id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            placeholder = _sql_placeholder(connection)
            # fetch details before deleting
            cursor.execute(_apply_placeholder('SELECT persona_id, tarjeta_uid, tarjeta_id FROM enrolar WHERE id = %s', connection), (id,))
            row = cursor.fetchone()
            persona_id = None
            tarjeta_uid = None
            tarjeta_pin = None
            if row:
                persona_id = row[0] if isinstance(row, (list, tuple)) else (row.get('persona_id') if hasattr(row, 'get') else None)
                tarjeta_uid = row[1] if isinstance(row, (list, tuple)) else (row.get('tarjeta_uid') if hasattr(row, 'get') else None)
                tarjeta_id = row[2] if isinstance(row, (list, tuple)) else (row.get('tarjeta_id') if hasattr(row, 'get') else None)
                # try to fetch pin from tarjetas if tarjeta_id available
                try:
                    if tarjeta_id:
                        cursor.execute(_apply_placeholder('SELECT pin FROM tarjetas WHERE id = %s', connection), (tarjeta_id,))
                        tp = cursor.fetchone()
                        if tp:
                            tarjeta_pin = tp[0] if isinstance(tp, (list, tuple)) else (tp.get('pin') if hasattr(tp, 'get') else None)
                except Exception:
                    pass
            cursor.execute(_apply_placeholder('DELETE FROM enrolar WHERE id = %s', connection), (id,))
            connection.commit()
            # insert history record for deletion
            try:
                hist_sql = "INSERT INTO historial_enrolamiento (enrolar_id, persona_id, nombre_persona, perfil, tarjeta_uid, tarjeta_pin, estado, responsable, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                if connection.__class__.__module__.startswith('sqlite3'):
                    hist_sql = hist_sql.replace('%s', '?')
                # try to get persona name
                nombre_persona = None
                try:
                    if persona_id:
                        cursor.execute(_apply_placeholder('SELECT nombre_completo FROM personas WHERE id = %s', connection), (persona_id,))
                        pn = cursor.fetchone()
                        if pn:
                            nombre_persona = pn[0] if isinstance(pn, (list, tuple)) else (pn.get('nombre_completo') if hasattr(pn, 'get') else None)
                except Exception:
                    pass
                hist_vals = (id, persona_id, nombre_persona, None, tarjeta_uid, tarjeta_pin, 'eliminado', session.get('usuario') if session else None, f'Enrolamiento eliminado id={id}')
                cursor.execute(_apply_placeholder(hist_sql, connection), hist_vals)
                connection.commit()
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
