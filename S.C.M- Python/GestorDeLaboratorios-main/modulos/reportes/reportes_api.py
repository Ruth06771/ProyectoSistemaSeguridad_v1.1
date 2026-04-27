from flask import Blueprint, request, jsonify
from config.db import get_connection

reportes_api = Blueprint('reportes_api', __name__)


# Reporte de historial de accesos
@reportes_api.route('/api/reportes/accesos_historial', methods=['GET'])
def accesos_historial():
    params = request.args
    filtros = []
    valores = []
    if params.get('fecha_desde'):
        filtros.append('fecha_hora >= %s')
        valores.append(params['fecha_desde'])
    if params.get('fecha_hasta'):
        filtros.append('fecha_hora <= %s')
        valores.append(params['fecha_hasta'])
    if params.get('tipo_accion'):
        filtros.append('accion = %s')
        valores.append(params['tipo_accion'])
    if params.get('usuario_responsable'):
        filtros.append('usuario_responsable LIKE %s')
        valores.append(f"%{params['usuario_responsable']}%")
    if params.get('tarjeta'):
        filtros.append('tarjeta LIKE %s')
        valores.append(f"%{params['tarjeta']}%")
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ''
    # Usar la tabla creada en config/db.py: historial_accesos
    sql = f"SELECT * FROM historial_accesos {where} ORDER BY fecha_hora DESC"
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            exec_sql = sql
            params = valores
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_sql = exec_sql.replace('%s', '?')
            cursor.execute(exec_sql, params)
            rows = cursor.fetchall()
            # Normalize rows into plain dicts. Use cursor.description to map tuple rows.
            cols = [c[0] for c in cursor.description] if cursor.description else []
            norm_rows = []
            for r in rows:
                if isinstance(r, dict):
                    norm_rows.append(r)
                    continue
                try:
                    # sqlite3.Row supports mapping protocol but not .get; dict() will work
                    norm_rows.append(dict(r))
                except Exception:
                    # tuple/list fallback: zip with column names
                    norm_rows.append({cols[i]: (r[i] if i < len(r) else None) for i in range(len(cols))})
            rows = norm_rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(rows)
    finally:
        connection.close()

# Reporte de historial de tarjetas
@reportes_api.route('/api/reportes/tarjetas_historial', methods=['GET'])
def tarjetas_historial():
    params = request.args
    filtros = []
    valores = []
    if params.get('fecha_desde'):
        filtros.append('fecha_hora >= %s')
        valores.append(params['fecha_desde'])
    if params.get('fecha_hasta'):
        filtros.append('fecha_hora <= %s')
        valores.append(params['fecha_hasta'])
    if params.get('accion'):
        filtros.append('accion = %s')
        valores.append(params['accion'])
    if params.get('usuario'):
        filtros.append('responsable LIKE %s')
        valores.append(f"%{params['usuario']}")
    if params.get('tarjeta'):
        filtros.append('uid LIKE %s')
        valores.append(f"%{params['tarjeta']}%")
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ''
    # Usar la tabla creada en config/db.py: historial_tarjetas
    sql = f"SELECT * FROM historial_tarjetas {where} ORDER BY fecha_hora DESC"
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            exec_sql = sql
            params = valores
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_sql = exec_sql.replace('%s', '?')
            cursor.execute(exec_sql, params)
            rows = cursor.fetchall()
            # Normalize rows into dicts using cursor.description as a fallback
            cols = [c[0] for c in cursor.description] if cursor.description else []
            norm_rows = []
            for r in rows:
                if isinstance(r, dict):
                    norm_rows.append(r)
                    continue
                try:
                    norm_rows.append(dict(r))
                except Exception:
                    norm_rows.append({cols[i]: (r[i] if i < len(r) else None) for i in range(len(cols))})
            # Normalize column names so frontend can rely on stable keys
            mapped = []
            for r in norm_rows:
                mapped.append({
                    'id': r.get('id'),
                    'uid_tarjeta': r.get('uid') or r.get('tarjeta') or r.get('tarjeta_uid'),
                    'nombre_usuario': r.get('nombre_completo') or r.get('nombre_usuario') or r.get('nombre'),
                    'accion': r.get('accion'),
                    'responsable': r.get('ejecutado_por') or r.get('responsable') or r.get('usuario'),
                    'descripcion': r.get('descripcion'),
                    'fecha_hora': r.get('fecha_hora')
                })
            rows = mapped
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(rows)
    finally:
        connection.close()


# Endpoint pequeño de métricas: contadores rápidos para dashboard
@reportes_api.route('/api/metrics', methods=['GET'])
def api_metrics():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            # Contar filas en tablas clave
            cursor.execute('SELECT COUNT(*) FROM personas')
            personas_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM tarjetas')
            tarjetas_count = cursor.fetchone()[0]
            # historial_accesos puede no existir en todas las instalaciones; manejar excepción
            try:
                cursor.execute('SELECT COUNT(*) FROM historial_accesos')
                accesos_count = cursor.fetchone()[0]
            except Exception:
                accesos_count = 0
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify({'personas': personas_count, 'tarjetas': tarjetas_count, 'accesos': accesos_count})
    finally:
        connection.close()


# Endpoint para listar movimientos (tipo de movimiento)
@reportes_api.route('/api/movimientos', methods=['GET'])
def api_movimientos():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, nombre, tipo, fecha_hora FROM movimientos ORDER BY fecha_hora DESC")
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                movimientos = [dict(r) for r in rows]
            else:
                # sqlite3.Row mapping
                movimientos = []
                for r in rows:
                    movimientos.append({
                        'id': r[0],
                        'nombre': r[1],
                        'tipo': r[2],
                        'fecha': str(r[3]) if r[3] is not None else None
                    })
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(movimientos)
    finally:
        connection.close()


# Endpoint para listar registros (tipo de registro) — usa tarjetas como base
@reportes_api.route('/api/registros', methods=['GET'])
def api_registros():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            # Seleccionamos uid y nombre desde tarjetas para mostrar como registros
            cursor.execute("SELECT id, nombre_completo AS nombre, uid FROM tarjetas ORDER BY id DESC")
            rows = cursor.fetchall()
            registros = []
            # Normalize rows to plain dicts when possible so we can use .get safely.
            if rows:
                # If rows[0] exposes mapping interface (has keys), convert all to dict
                if hasattr(rows[0], 'keys'):
                    rows = [dict(r) for r in rows]
            # Now map to the registro shape, handling tuple-style rows as a fallback
            for r in rows:
                if isinstance(r, dict):
                    id_ = r.get('id')
                    nombre = r.get('nombre')
                else:
                    # tuple/list fallback (id, nombre, uid)
                    id_ = r[0] if len(r) > 0 else None
                    nombre = r[1] if len(r) > 1 else None
                registros.append({'id': id_, 'nombre': nombre, 'metodo': 'RFID'})
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(registros)
    finally:
        connection.close()
