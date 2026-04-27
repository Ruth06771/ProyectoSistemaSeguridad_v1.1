from flask import Blueprint, request, jsonify
from config.db import get_connection

dispositivos_api = Blueprint('dispositivos_api', __name__)


@dispositivos_api.route('/api/dispositivos', methods=['GET'])
def list_dispositivos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Prefer snake_case schema for runtime (matches config/db.py)
        if conn.__class__.__module__.startswith('sqlite3'):
            # check whether snake_case table exists; if not, fall back to PascalCase
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispositivos'")
            if cur.fetchone():
                cur.execute('SELECT id, nombre, api_key, activo, fecha_registro FROM dispositivos')
                rows = cur.fetchall()
                results = [dict(zip(['id','nombre','api_key','activo','fecha_registro'], r)) for r in rows]
            else:
                # fallback to legacy PascalCase table
                cur.execute('SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos')
                rows = cur.fetchall()
                results = [dict(zip(['id','nombre','api_key','activo','fecha_registro'], r)) for r in rows]
        else:
            # For non-sqlite (MySQL/MSSQL) try to select snake_case first, fall back to PascalCase
            try:
                cur.execute('SELECT id, nombre, api_key, activo, fecha_registro FROM dispositivos')
                rows = cur.fetchall()
                results = rows
            except Exception:
                cur.execute('SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos')
                rows = cur.fetchall()
                results = rows
        return jsonify(results)
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


@dispositivos_api.route('/api/dispositivos/<int:did>', methods=['GET'])
def get_dispositivo(did):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispositivos'")
            if cur.fetchone():
                cur.execute('SELECT id, nombre, api_key, activo, fecha_registro FROM dispositivos WHERE id = ?', (did,))
                row = cur.fetchone()
                if not row:
                    return jsonify({'error':'no encontrado'}), 404
                return jsonify(dict(zip(['id','nombre','api_key','activo','fecha_registro'], row)))
            else:
                cur.execute('SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos WHERE IdDispositivo = ?', (did,))
                row = cur.fetchone()
                if not row:
                    return jsonify({'error':'no encontrado'}), 404
                return jsonify(dict(zip(['id','nombre','api_key','activo','fecha_registro'], row)))
        else:
            try:
                cur.execute('SELECT id, nombre, api_key, activo, fecha_registro FROM dispositivos WHERE id = %s', (did,))
                row = cur.fetchone()
            except Exception:
                cur.execute('SELECT IdDispositivo AS id, Nombre AS nombre, ApiKey AS api_key, Activo AS activo, FechaRegistro AS fecha_registro FROM Dispositivos WHERE IdDispositivo = %s', (did,))
                row = cur.fetchone()
            if not row:
                return jsonify({'error':'no encontrado'}), 404
            return jsonify(row)
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


@dispositivos_api.route('/api/dispositivos', methods=['POST'])
def create_dispositivo():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    apikey = data.get('apikey')
    if not nombre or not apikey:
        return jsonify({'error':'nombre y apikey requeridos'}), 400
    conn = get_connection()
    cur = conn.cursor()
    try:
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute('INSERT INTO dispositivos (nombre,api_key,activo) VALUES (?,?,1)', (nombre, apikey))
            conn.commit()
            return jsonify({'success': True, 'id': cur.lastrowid})
        else:
            try:
                cur.execute('INSERT INTO dispositivos (nombre,api_key,activo) VALUES (%s,%s,1)', (nombre, apikey))
                conn.commit()
                return jsonify({'success': True})
            except Exception:
                cur.execute('INSERT INTO Dispositivos (Nombre,ApiKey,Activo) VALUES (%s,%s,1)', (nombre, apikey))
                conn.commit()
                return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


@dispositivos_api.route('/api/dispositivos/<int:did>/activar', methods=['PUT'])
def activar_dispositivo(did):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute('UPDATE dispositivos SET activo = 1 WHERE id = ?', (did,))
        else:
            try:
                cur.execute('UPDATE dispositivos SET activo = 1 WHERE id = %s', (did,))
            except Exception:
                cur.execute('UPDATE Dispositivos SET Activo = 1 WHERE IdDispositivo = %s', (did,))
        conn.commit()
        return jsonify({'success': True})
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


@dispositivos_api.route('/api/dispositivos/<int:did>/desactivar', methods=['PUT'])
def desactivar_dispositivo(did):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute('UPDATE dispositivos SET activo = 0 WHERE id = ?', (did,))
        else:
            try:
                cur.execute('UPDATE dispositivos SET activo = 0 WHERE id = %s', (did,))
            except Exception:
                cur.execute('UPDATE Dispositivos SET Activo = 0 WHERE IdDispositivo = %s', (did,))
        conn.commit()
        return jsonify({'success': True})
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
