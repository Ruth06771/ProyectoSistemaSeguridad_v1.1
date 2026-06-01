from flask import Blueprint, request, jsonify, session
from config.db import get_connection, log_action
import datetime
import os
import traceback

esp_api = Blueprint('esp_api', __name__)


def verificar_acceso_credencial(uid=None, pin=None):
    """Verificar si un UID o PIN existe en tarjetas y si el usuario está enrolado (estado = 1)."""
    if not uid and not pin:
        return {
            'permitido': False,
            'mensaje': 'Se requiere uid o pin.',
            'uid': uid,
            'pin': pin,
            'enrolado': None,
            'tarjeta_id': None,
            'tarjeta_uid': None,
            'tarjeta_pin': None,
            'credencial': None
        }

    # Limpiar UIDs (eliminar espacios en blanco)
    if uid:
        uid = uid.strip() if isinstance(uid, str) else uid
    if pin:
        pin = str(pin).strip() if pin else pin

    conn = get_connection()
    cur = conn.cursor()
    try:
        is_sqlite = cur.__class__.__module__.startswith('sqlite3')

        tarjeta_row = None
        credencial = None
        if uid:
            if is_sqlite:
                cur.execute('SELECT id, uid, pin FROM tarjetas WHERE uid = ? LIMIT 1', (uid,))
            else:
                cur.execute('SELECT id, uid, pin FROM tarjetas WHERE uid = %s LIMIT 1', (uid,))
            tarjeta_row = cur.fetchone()
            credencial = 'TARJETA'

        if not tarjeta_row and pin:
            if is_sqlite:
                cur.execute('SELECT id, uid, pin FROM tarjetas WHERE pin = ? LIMIT 1', (pin,))
            else:
                cur.execute('SELECT id, uid, pin FROM tarjetas WHERE pin = %s LIMIT 1', (pin,))
            tarjeta_row = cur.fetchone()
            credencial = 'PIN'

        if not tarjeta_row:
            if not credencial:
                credencial = 'TARJETA' if uid else 'PIN' if pin else None
            return {
                'permitido': False,
                'mensaje': 'Tarjeta/PIN no encontrado.',
                'uid': uid,
                'pin': pin,
                'enrolado': 0,
                'tarjeta_id': None,
                'tarjeta_uid': None,
                'tarjeta_pin': None,
                'credencial': credencial
            }

        try:
            tarjeta_id = tarjeta_row['id']
            tarjeta_uid = tarjeta_row['uid']
            tarjeta_pin = tarjeta_row['pin']
        except Exception:
            tarjeta_id = tarjeta_row[0]
            tarjeta_uid = tarjeta_row[1] if len(tarjeta_row) > 1 else None
            tarjeta_pin = tarjeta_row[2] if len(tarjeta_row) > 2 else None

        # Robustez en la búsqueda de enrolamiento (Usa UID limpio, mayúsculas y acepta estado = 1 o NULL)
        enrollment_active = False
        
        if tarjeta_uid:
            if is_sqlite:
                cur.execute(
                    'SELECT id, estado FROM enrolar WHERE UPPER(TRIM(tarjeta_uid)) = UPPER(TRIM(?)) AND (estado = 1 OR estado IS NULL) LIMIT 1',
                    (tarjeta_uid,)
                )
            else:
                cur.execute(
                    'SELECT id, estado FROM enrolar WHERE UPPER(TRIM(tarjeta_uid)) = UPPER(TRIM(%s)) AND (estado = 1 OR estado IS NULL) LIMIT 1',
                    (tarjeta_uid,)
                )
            enrolar_row = cur.fetchone()
            if enrolar_row:
                try:
                    estado = enrolar_row['estado']
                except Exception:
                    estado = enrolar_row[1]
                enrollment_active = (estado == 1 or estado is None)
        
        # Fallback por tarjeta_id si no se encuentra por UID
        if not enrollment_active and tarjeta_id:
            if is_sqlite:
                cur.execute(
                    'SELECT id, estado FROM enrolar WHERE tarjeta_id = ? AND (estado = 1 OR estado IS NULL) LIMIT 1',
                    (tarjeta_id,)
                )
            else:
                cur.execute(
                    'SELECT id, estado FROM enrolar WHERE tarjeta_id = %s AND (estado = 1 OR estado IS NULL) LIMIT 1',
                    (tarjeta_id,)
                )
            enrolar_row = cur.fetchone()
            if enrolar_row:
                try:
                    estado = enrolar_row['estado']
                except Exception:
                    estado = enrolar_row[1]
                enrollment_active = (estado == 1 or estado is None)

        return {
            'permitido': enrollment_active,
            'mensaje': 'Acceso permitido: credencial válida y enrolada.' if enrollment_active else 'Credencial válida pero usuario no enrolado.',
            'uid': tarjeta_uid,
            'pin': tarjeta_pin,
            'enrolado': 1 if enrollment_active else 0,
            'tarjeta_id': tarjeta_id,
            'tarjeta_uid': tarjeta_uid,
            'tarjeta_pin': tarjeta_pin,
            'credencial': credencial
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


@esp_api.route('/api/esp/access', methods=['POST'])
def esp_access():
    """Endpoint para que un ESP32 envíe un evento de acceso."""
    data = request.get_json(silent=True) or {}
    uid = data.get('uid')
    pin = data.get('pin')
    device = data.get('device') or request.remote_addr
    ts = data.get('timestamp') or datetime.datetime.utcnow().isoformat()
    
    # Identificar la acción que viene del ESP32
    esp_action = data.get('accion')
    if not esp_action or not str(esp_action).strip():
        esp_action = 'LECTURA'
    else:
        esp_action = str(esp_action).strip().upper()

    # Validación de API key
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'success': False, 'error': 'X-API-Key header requerido'}), 401

    try:
        conn_check = get_connection()
        cur_check = conn_check.cursor()
        is_sqlite_check = cur_check.__class__.__module__.startswith('sqlite3')
        dispositivos_table_exists = False
        try:
            if is_sqlite_check:
                cur_check.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispositivos'")
                dispositivos_table_exists = bool(cur_check.fetchone())
                if not dispositivos_table_exists:
                    cur_check.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Dispositivos'")
                    dispositivos_table_exists = bool(cur_check.fetchone())
            else:
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

    if not uid and not pin:
        return jsonify({'success': False, 'error': 'uid o pin requerido'}), 400

    # Ejecutamos la lógica de verificación robusta
    access_result = verificar_acceso_credencial(uid=uid, pin=pin)
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        is_sqlite = cur.__class__.__module__.startswith('sqlite3')

        if uid:
            uid = uid.strip()
            if is_sqlite:
                cur.execute('SELECT id, uid FROM tarjetas WHERE uid = ? LIMIT 1', (uid,))
            else:
                cur.execute('SELECT id, uid FROM tarjetas WHERE uid = %s LIMIT 1', (uid,))
        else:
            if is_sqlite:
                cur.execute('SELECT id, uid FROM tarjetas WHERE pin = ? LIMIT 1', (pin,))
            else:
                cur.execute('SELECT id, uid FROM tarjetas WHERE pin = %s LIMIT 1', (pin,))
        row = cur.fetchone()

        tarjeta_id = None
        tarjeta_uid_lookup = uid
        existed = False
        if row:
            try:
                tarjeta_id = row['id']
                tarjeta_uid_lookup = row['uid']
            except Exception:
                tarjeta_id = row[0]
                tarjeta_uid_lookup = row[1] if len(row) > 1 else uid
            existed = True
        elif uid:
            if is_sqlite:
                cur.execute('INSERT INTO tarjetas (uid, fecha_registro) VALUES (?, datetime("now"))', (uid,))
                conn.commit()
                tarjeta_id = cur.lastrowid
            else:
                cur.execute('INSERT INTO tarjetas (uid, fecha_registro) VALUES (%s, NOW())', (uid,))
                conn.commit()
                cur.execute('SELECT id FROM tarjetas WHERE uid = %s LIMIT 1', (uid,))
                rid = cur.fetchone()
                tarjeta_id = rid['id'] if isinstance(rid, dict) and 'id' in rid else (rid[0] if rid else None)

        # En este endpoint ESP, el acceso se almacena en registro_acceso y no debe irrumpir
        # en el historial de tarjetas como una acción de tarjeta normal.
        persona_info = None
        perfil_info = None
        enrolar_id = None
        
        search_tarjeta_id = access_result.get('tarjeta_id')
        search_tarjeta_uid = access_result.get('tarjeta_uid')
        
        try:
            if search_tarjeta_id is not None or search_tarjeta_uid is not None:
                if is_sqlite:
                    cur.execute(
                        'SELECT id, persona_id FROM enrolar WHERE (UPPER(TRIM(tarjeta_uid)) = UPPER(TRIM(?)) OR tarjeta_id = ?) AND (estado = 1 OR estado IS NULL) LIMIT 1',
                        (search_tarjeta_uid, search_tarjeta_id)
                    )
                else:
                    cur.execute(
                        'SELECT id, persona_id FROM enrolar WHERE (UPPER(TRIM(tarjeta_uid)) = UPPER(TRIM(%s)) OR tarjeta_id = %s) AND (estado = 1 OR estado IS NULL) LIMIT 1',
                        (search_tarjeta_uid, search_tarjeta_id)
                    )
                er = cur.fetchone()
                
                if er:
                    try:
                        enrolar_id = er['id'] if isinstance(er, dict) else er[0]
                        pid = er['persona_id'] if isinstance(er, dict) else er[1]
                    except Exception:
                        enrolar_id = er[0]
                        pid = er[1]
                    
                    if pid:
                        if is_sqlite:
                            cur.execute('SELECT * FROM personas WHERE id = ? LIMIT 1', (pid,))
                        else:
                            cur.execute('SELECT * FROM personas WHERE id = %s LIMIT 1', (pid,))
                        persona_row = cur.fetchone()
                        if persona_row:
                            try:
                                persona_info = dict(persona_row)
                            except Exception:
                                cols = [c[0] for c in cur.description] if cur.description else []
                                persona_info = {cols[i]: persona_row[i] for i in range(min(len(cols), len(persona_row)))}
                        
                        if is_sqlite:
                            cur.execute('SELECT * FROM perfiles WHERE persona_id = ? ORDER BY fecha_creacion DESC', (pid,))
                        else:
                            cur.execute('SELECT * FROM perfiles WHERE persona_id = %s ORDER BY fecha_creacion DESC', (pid,))
                        perfiles = cur.fetchall()
                        if perfiles:
                            try:
                                perfil_info = [dict(p) for p in perfiles]
                            except Exception:
                                cols = [c[0] for c in cur.description] if cur.description else []
                                perfil_info = [{cols[i]: p[i] for i in range(min(len(cols), len(p)))} for p in perfiles]
                        
                        # --- MODIFICACIÓN DEL CONTROL DE ACCESOS ---
                        resultado = 'Permitido' if access_result['permitido'] else 'Denegado'
                        registro_tarjeta_uid = search_tarjeta_uid or (uid if uid else None)
                        credencial = access_result.get('credencial') or ('PIN' if pin else 'TARJETA')
                        
                        # Determinar el tipo de movimiento y armar la descripción exacta solicitada
                        tipo_movimiento_id = 1
                        tipo_movimiento_nombre = 'salida' if esp_action == 'DEVOLVER' else 'entrada'
                        accion_legible = 'RETIRANDO' if esp_action == 'RETIRAR' else 'DEVOLVIENDO' if esp_action == 'DEVOLVER' else esp_action
                        
                        # Aquí agregamos la descripción clara al Control de Accesos
                        control_acceso_descripcion = f'El usuario está {accion_legible} un equipo. (Disp: {device})'
                        
                        try:
                            if is_sqlite:
                                cur.execute('SELECT id FROM tipo_movimiento WHERE LOWER(TRIM(movimiento)) = ?', (tipo_movimiento_nombre,))
                            else:
                                cur.execute('SELECT id FROM tipo_movimiento WHERE LOWER(TRIM(movimiento)) = %s', (tipo_movimiento_nombre,))
                            tm_row = cur.fetchone()
                            if tm_row:
                                tipo_movimiento_id = tm_row[0] if isinstance(tm_row, (tuple, list)) else tm_row.get('id')
                        except Exception:
                            pass
                        
                        # Guardar el resultado del ESP en registro_acceso
                        if is_sqlite:
                            cur.execute('INSERT INTO registro_acceso (enrolar_id, tarjeta_uid, fecha_hora, tipo_movimiento_id, resultado, credencial, descripcion, accion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                        (enrolar_id, registro_tarjeta_uid, ts, tipo_movimiento_id, resultado, credencial, control_acceso_descripcion, esp_action))
                        else:
                            cur.execute('INSERT INTO registro_acceso (enrolar_id, tarjeta_uid, fecha_hora, tipo_movimiento_id, resultado, credencial, descripcion, accion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                        (enrolar_id, registro_tarjeta_uid, ts, tipo_movimiento_id, resultado, credencial, control_acceso_descripcion, esp_action))
                        try:
                            conn.commit()
                        except Exception:
                            pass
        except Exception:
            traceback.print_exc()

        if not access_result['permitido']:
            persona_info = None
            perfil_info = None

        return jsonify({
            'success': True,
            'uid': uid,
            'tarjeta_id': tarjeta_id,
            'existed': existed,
            'persona': persona_info,
            'perfiles': perfil_info,
            'access': access_result
        })

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