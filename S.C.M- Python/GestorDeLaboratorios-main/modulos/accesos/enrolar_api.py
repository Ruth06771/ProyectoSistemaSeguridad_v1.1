from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import traceback
import sqlite3

enrolar_api = Blueprint('enrolar_api', __name__)


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

            # Insert enrolar record linking persona and tarjeta (uses tarjeta_uid)
            try:
                enrolar_sql = "INSERT INTO enrolar (persona_id, tarjeta_uid, perfil_acceso_lab_id) VALUES (%s, %s, %s)"
                enrolar_vals = (persona_id, tarjeta.get('uid'), perfil.get('perfil_acceso_lab_id') if perfil and isinstance(perfil, dict) else None)
                if conn.__class__.__module__.startswith('sqlite3'):
                    enrolar_sql = enrolar_sql.replace('%s', '?')
                cur.execute(enrolar_sql, enrolar_vals)
                enrolar_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
            except Exception:
                # non-critical, continue but set enrolar_id to None
                enrolar_id = None

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
