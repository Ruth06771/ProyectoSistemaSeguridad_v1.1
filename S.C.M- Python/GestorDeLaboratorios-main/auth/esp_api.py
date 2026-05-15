from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import datetime
import os
import traceback

esp_api = Blueprint('esp_api', __name__)


@esp_api.route('/api/esp/access', methods=['POST'])
def esp_access():
    """Endpoint para que un ESP32 envíe un evento de acceso.
    JSON esperado: {"uid": "UID123", "device": "Controladora-1", "timestamp": "2025-10-07T12:00:00Z"}
    """
    data = request.get_json(silent=True) or {}
    uid = data.get('uid')
    device = data.get('device') or request.remote_addr
    ts = data.get('timestamp') or datetime.datetime.utcnow().isoformat()

    # API key validation
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'success': False, 'error': 'X-API-Key header requerido'}), 401

    # Validate api_key against dispositivos table (snake_case) if present, otherwise fall back to env var
    try:
        conn_check = get_connection()
        cur_check = conn_check.cursor()
        is_sqlite_check = cur_check.__class__.__module__.startswith('sqlite3')
        dispositivos_table_exists = False
        try:
            if is_sqlite_check:
                # check for snake_case first
                cur_check.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispositivos'")
                dispositivos_table_exists = bool(cur_check.fetchone())
                if not dispositivos_table_exists:
                    # fall back to PascalCase table name if present
                    cur_check.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Dispositivos'")
                    dispositivos_table_exists = bool(cur_check.fetchone())
            else:
                # try snake_case first
                try:
                    cur_check.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'dispositivos'")
                    dispositivos_table_exists = bool(cur_check.fetchone())
                except Exception:
                    cur_check.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Dispositivos'")
                    dispositivos_table_exists = bool(cur_check.fetchone())
        except Exception:
            dispositivos_table_exists = False

        valid_key = False
        if dispositivos_table_exists:
            try:
                if is_sqlite_check:
                    # prefer snake_case
                    try:
                        cur_check.execute('SELECT id FROM dispositivos WHERE api_key = ? AND activo = 1', (api_key,))
                        found = cur_check.fetchone()
                    except Exception:
                        cur_check.execute('SELECT IdDispositivo FROM Dispositivos WHERE ApiKey = ? AND Activo = 1', (api_key,))
                        found = cur_check.fetchone()
                else:
                    try:
                        cur_check.execute('SELECT id FROM dispositivos WHERE api_key = %s AND activo = 1', (api_key,))
                        found = cur_check.fetchone()
                    except Exception:
                        cur_check.execute('SELECT IdDispositivo FROM Dispositivos WHERE ApiKey = %s AND Activo = 1', (api_key,))
                        found = cur_check.fetchone()
                valid_key = bool(found)
            except Exception:
                valid_key = False
        else:
            # fallback to environment variable
            valid_key = (api_key == os.environ.get('ESP_API_KEY'))

    except Exception:
        valid_key = (api_key == os.environ.get('ESP_API_KEY'))
    finally:
        try:
            cur_check.close()
        except Exception:
            pass
        try:
            conn_check.close()
        except Exception:
            pass

    if not valid_key:
        return jsonify({'success': False, 'error': 'X-API-Key inválida'}), 401

    if not uid:
        return jsonify({'success': False, 'error': 'uid requerido'}), 400

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Detect placeholder for param style
        is_sqlite = cur.__class__.__module__.startswith('sqlite3')

        # Check if tarjeta exists
        if is_sqlite:
            cur.execute('SELECT id, uid FROM tarjetas WHERE uid = ?', (uid,))
            row = cur.fetchone()
        else:
            cur.execute('SELECT id, uid FROM tarjetas WHERE uid = %s', (uid,))
            row = cur.fetchone()

        tarjeta_id = None
        existed = False
        if row:
            # sqlite row can be sqlite3.Row or a tuple depending on driver
            try:
                tarjeta_id = row['id']
            except Exception:
                tarjeta_id = row[0]
            existed = True
        else:
            # insert tarjeta
            if is_sqlite:
                cur.execute('INSERT INTO tarjetas (uid, fecha_registro) VALUES (?, datetime("now"))', (uid,))
                conn.commit()
                tarjeta_id = cur.lastrowid
            else:
                cur.execute('INSERT INTO tarjetas (uid, fecha_registro) VALUES (%s, NOW())', (uid,))
                conn.commit()
                # try to fetch inserted id
                cur.execute('SELECT id FROM tarjetas WHERE uid = %s', (uid,))
                rid = cur.fetchone()
                tarjeta_id = rid['id'] if isinstance(rid, dict) and 'id' in rid else (rid[0] if rid else None)

        # Insert into historial_tarjetas for audit
        descripcion = f'Acceso recibido desde {device} at {ts}'
        if is_sqlite:
            cur.execute('INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion) VALUES (?, ?, ?, ?, ?, ?)',
                        (tarjeta_id, uid, None, 'acceso', device, descripcion))
        else:
            cur.execute('INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                        (tarjeta_id, uid, None, 'acceso', device, descripcion))
        try:
            conn.commit()
        except Exception:
            pass

        # Check if tarjeta is already linked to a persona via enrolar table
        persona_info = None
        perfil_info = None
        enrolar_id = None
        try:
            if is_sqlite:
                cur.execute('SELECT id, persona_id FROM enrolar WHERE tarjeta_uid = ? LIMIT 1', (uid,))
                er = cur.fetchone()
            else:
                cur.execute('SELECT id, persona_id FROM enrolar WHERE tarjeta_uid = %s LIMIT 1', (uid,))
                er = cur.fetchone()
            if er:
                try:
                    enrolar_id = er['id'] if isinstance(er, dict) else er[0]
                    pid = er['persona_id'] if isinstance(er, dict) else er[1]
                except Exception:
                    enrolar_id = er[0]
                    pid = er[1]
                if pid:
                    # fetch persona
                    if is_sqlite:
                        cur.execute('SELECT * FROM personas WHERE id = ? LIMIT 1', (pid,))
                        persona_row = cur.fetchone()
                    else:
                        cur.execute('SELECT * FROM personas WHERE id = %s LIMIT 1', (pid,))
                        persona_row = cur.fetchone()
                    if persona_row:
                        try:
                            # try dict-like access
                            persona_info = dict(persona_row)
                        except Exception:
                            # tuple -> map columns roughly by fetching description
                            cols = [c[0] for c in cur.description] if cur.description else []
                            persona_info = {cols[i]: persona_row[i] for i in range(min(len(cols), len(persona_row)))}
                    # attempt to fetch perfil(s)
                    if is_sqlite:
                        cur.execute('SELECT * FROM perfiles WHERE persona_id = ? ORDER BY fecha_creacion DESC', (pid,))
                        perfiles = cur.fetchall()
                    else:
                        cur.execute('SELECT * FROM perfiles WHERE persona_id = %s ORDER BY fecha_creacion DESC', (pid,))
                        perfiles = cur.fetchall()
                    if perfiles:
                        try:
                            perfil_info = [dict(p) for p in perfiles]
                        except Exception:
                            cols = [c[0] for c in cur.description] if cur.description else []
                            perfil_info = [{cols[i]: p[i] for i in range(min(len(cols), len(p)))} for p in perfiles]
                    
                    # Register access in registro_acceso table
                    resultado = 'Permitido' if persona_info else 'Denegado'
                    credencial = data.get('credencial', 'Tarjeta')  # 'Tarjeta' o 'PIN'
                    tipo_movimiento_id = 1  # Default: Entrada (should be fetched from tipo_movimiento)
                    
                    # Get tipo_movimiento_id for 'Entrada'
                    try:
                        if is_sqlite:
                            cur.execute('SELECT id FROM tipo_movimiento WHERE nombre = ?', ('Entrada',))
                        else:
                            cur.execute('SELECT id FROM tipo_movimiento WHERE nombre = %s', ('Entrada',))
                        tm_row = cur.fetchone()
                        if tm_row:
                            tipo_movimiento_id = tm_row[0] if isinstance(tm_row, (tuple, list)) else tm_row.get('id')
                    except Exception:
                        pass
                    
                    if is_sqlite:
                        cur.execute('INSERT INTO registro_acceso (enrolar_id, tarjeta_uid, fecha_hora, tipo_movimiento_id, resultado, credencial, descripcion) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                    (enrolar_id, uid, ts, tipo_movimiento_id, resultado, credencial, descripcion))
                    else:
                        cur.execute('INSERT INTO registro_acceso (enrolar_id, tarjeta_uid, fecha_hora, tipo_movimiento_id, resultado, credencial, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                                    (enrolar_id, uid, ts, tipo_movimiento_id, resultado, credencial, descripcion))
                    try:
                        conn.commit()
                    except Exception:
                        pass
        except Exception:
            # non-fatal
            traceback.print_exc()

        # If tarjeta not linked and request includes persona/perfil, try to enrol automatically
        if not persona_info:
            incoming_persona = data.get('persona')
            incoming_perfil = data.get('perfil')
            if incoming_persona:
                try:
                    # Basic insert/update persona similar to enrolar_api behavior
                    campos = ['nombre_completo', 'fecha_nacimiento', 'correo', 'telefono_personal', 'documento_identidad', 'sexo', 'tipo_sangre', 'rol']
                    valores = [incoming_persona.get(c) for c in campos]
                    placeholder = '?'
                    if not is_sqlite:
                        placeholder = '%s'
                    pid = None
                    # try match by documento_identidad
                    if incoming_persona.get('documento_identidad'):
                        try:
                            if is_sqlite:
                                cur.execute(f"SELECT id FROM personas WHERE documento_identidad = {placeholder} LIMIT 1", (incoming_persona.get('documento_identidad'),))
                            else:
                                cur.execute(f"SELECT id FROM personas WHERE documento_identidad = {placeholder} LIMIT 1", (incoming_persona.get('documento_identidad'),))
                            r = cur.fetchone()
                            if r:
                                pid = r[0] if isinstance(r, (list, tuple)) else (r.get('id') if hasattr(r, 'get') else None)
                        except Exception:
                            pass
                    # fallback insert
                    if not pid:
                        sql = f"INSERT INTO personas ({', '.join(campos)}) VALUES ({', '.join([placeholder]*len(campos))})"
                        try:
                            cur.execute(sql, valores)
                            conn.commit()
                            pid = cur.lastrowid if hasattr(cur, 'lastrowid') else None
                            if pid:
                                try:
                                    log_action(conn, 'personas', entidad_id=pid, entidad_tipo='persona', accion='create', usuario=None, descripcion=f'Persona creada vía ESP32 uid={uid}')
                                except Exception:
                                    pass
                        except Exception:
                            try:
                                conn.rollback()
                            except Exception:
                                pass
                    # create perfil if provided
                    perfil_id = None
                    if incoming_perfil and pid:
                        try:
                            if is_sqlite:
                                cur.execute('INSERT INTO perfiles (persona_id, nombre, datos) VALUES (?, ?, ?)', (pid, incoming_perfil.get('nombre'), incoming_perfil.get('datos')))
                            else:
                                cur.execute('INSERT INTO perfiles (persona_id, nombre, datos) VALUES (%s, %s, %s)', (pid, incoming_perfil.get('nombre'), incoming_perfil.get('datos')))
                            perfil_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
                            conn.commit()
                        except Exception:
                            try:
                                conn.rollback()
                            except Exception:
                                pass
                    # finally insert enrolar linking persona and tarjeta uid
                    if pid:
                        try:
                            if is_sqlite:
                                cur.execute('INSERT INTO enrolar (persona_id, tarjeta_uid, perfil_acceso_lab_id) VALUES (?, ?, ?)', (pid, uid, None))
                            else:
                                cur.execute('INSERT INTO enrolar (persona_id, tarjeta_uid, perfil_acceso_lab_id) VALUES (%s, %s, %s)', (pid, uid, None))
                            conn.commit()
                            persona_info = {}
                            try:
                                # fetch inserted persona
                                if is_sqlite:
                                    cur.execute('SELECT * FROM personas WHERE id = ? LIMIT 1', (pid,))
                                else:
                                    cur.execute('SELECT * FROM personas WHERE id = %s LIMIT 1', (pid,))
                                prow = cur.fetchone()
                                if prow:
                                    persona_info = dict(prow) if hasattr(prow, 'keys') else {col[0]: prow[i] for i, col in enumerate(cur.description)}
                            except Exception:
                                pass
                        except Exception:
                            try:
                                conn.rollback()
                            except Exception:
                                pass
                except Exception:
                    traceback.print_exc()

        return jsonify({'success': True, 'uid': uid, 'tarjeta_id': tarjeta_id, 'existed': existed, 'persona': persona_info, 'perfiles': perfil_info})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
