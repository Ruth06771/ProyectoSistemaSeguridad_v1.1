from flask import Blueprint, request, jsonify
from config.db import get_connection

reportes_api = Blueprint('reportes_api', __name__)

ALLOWED_TARJETA_ACCIONES = {
    'alta': ('alta', 'creada', 'activo'),
    'baja': ('baja', 'inactivo', 'desactivado'),
    'editada': ('editada', 'editado', 'edicion', 'modificada'),
    'eliminada': ('eliminada', 'eliminado')
}


def normalize_tarjeta_accion(accion):
    if not accion:
        return None
    raw = accion.strip().lower()
    if raw in ALLOWED_TARJETA_ACCIONES['alta']:
        return 'alta'
    if raw in ALLOWED_TARJETA_ACCIONES['baja']:
        return 'baja'
    if raw in ALLOWED_TARJETA_ACCIONES['editada']:
        return 'editada'
    if raw in ALLOWED_TARJETA_ACCIONES['eliminada']:
        return 'eliminada'
    return None



# Reporte de historial de accesos (desde registro_acceso)
@reportes_api.route('/api/reportes/accesos_historial', methods=['GET'])
def accesos_historial():
    params = request.args
    filtros = []
    valores = []
    
    if params.get('fecha_desde'):
        filtros.append('ra.fecha_hora >= ?')
        valores.append(f"{params['fecha_desde']} 00:00:00")
    if params.get('fecha_hasta'):
        filtros.append('ra.fecha_hora <= ?')
        valores.append(f"{params['fecha_hasta']} 23:59:59")
    if params.get('resultado'):
        filtros.append('ra.resultado = ?')
        valores.append(params['resultado'])
    if params.get('credencial'):
        credencial_val = params['credencial'].strip().lower()
        if credencial_val == 'tarjeta':
            filtros.append("LOWER(TRIM(ra.credencial)) IN ('tarjeta', 'uid')")
        elif credencial_val == 'pin':
            filtros.append("LOWER(TRIM(ra.credencial)) = 'pin'")
        else:
            filtros.append('LOWER(TRIM(ra.credencial)) = ?')
            valores.append(credencial_val)

    if params.get('accion'):
        filtros.append('LOWER(TRIM(ra.accion)) = ?')
        valores.append(params['accion'].strip().lower())
    elif params.get('tipo_movimiento'):
        filtros.append('LOWER(TRIM(tm.movimiento)) = ?')
        valores.append(params['tipo_movimiento'].strip().lower())
    
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ''
    
    # Query: Lee de registro_acceso y hace JOIN con enrolar/personas/tipo_movimiento
    sql = f"""
    SELECT 
        ra.id,
        ra.fecha_hora,
        CASE
            WHEN p.nombre_completo IS NOT NULL THEN p.nombre_completo
            WHEN ra.enrolar_id IS NULL THEN 'Usuario No Registrado'
            ELSE 'Desconocido'
        END AS persona,
        CASE
            WHEN LOWER(TRIM(tm.movimiento)) = 'entrada' THEN 'Entrada'
            WHEN LOWER(TRIM(tm.movimiento)) = 'salida' THEN 'Salida'
            WHEN LOWER(ra.descripcion) LIKE '%retirar%' THEN 'Entrada'
            WHEN LOWER(ra.descripcion) LIKE '%devolver%' THEN 'Salida'
            ELSE COALESCE(tm.movimiento, ra.descripcion, 'Desconocido')
        END AS movimiento,
        COALESCE(ra.resultado, 'Registrado') AS resultado,
        CASE
            WHEN LOWER(TRIM(COALESCE(ra.credencial, 'Tarjeta'))) IN ('uid', 'tarjeta') THEN 'TARJETA'
            WHEN LOWER(TRIM(ra.credencial)) = 'pin' THEN 'PIN'
            ELSE UPPER(ra.credencial)
        END AS credencial,
        ra.tarjeta_uid,
        ra.accion,
        ra.descripcion
    FROM registro_acceso ra
    LEFT JOIN enrolar e ON ra.enrolar_id = e.id
    LEFT JOIN personas p ON e.persona_id = p.id
    LEFT JOIN tipo_movimiento tm ON ra.tipo_movimiento_id = tm.id
    {where}
    ORDER BY ra.fecha_hora DESC
    """
    
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(sql, valores)
            rows = cursor.fetchall()
            
            # Normalize rows into plain dicts
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
        filtros.append('fecha_hora >= ?')
        valores.append(f"{params['fecha_desde']} 00:00:00")
    if params.get('fecha_hasta'):
        filtros.append('fecha_hora <= ?')
        valores.append(f"{params['fecha_hasta']} 23:59:59")
    if params.get('accion'):
        accion_valor = params['accion'].strip().lower()
        if accion_valor in ALLOWED_TARJETA_ACCIONES['alta']:
            filtros.append("LOWER(TRIM(ht.accion)) IN ('alta', 'creada', 'activo')")
        elif accion_valor in ALLOWED_TARJETA_ACCIONES['baja']:
            filtros.append("LOWER(TRIM(ht.accion)) IN ('baja', 'inactivo', 'desactivado')")
        elif accion_valor in ALLOWED_TARJETA_ACCIONES['editada']:
            filtros.append("LOWER(TRIM(ht.accion)) IN ('editada', 'editado', 'edicion', 'modificada')")
        elif accion_valor in ALLOWED_TARJETA_ACCIONES['eliminada']:
            filtros.append("LOWER(TRIM(ht.accion)) IN ('eliminada', 'eliminado')")
        else:
            filtros.append('1 = 0')
    if params.get('usuario'):
        filtros.append('ht.ejecutado_por LIKE ?')
        valores.append(f"%{params['usuario']}%")
    if params.get('tarjeta'):
        filtros.append('(ht.uid LIKE ? OR t.uid LIKE ?)')
        valores.append(f"%{params['tarjeta']}%")
        valores.append(f"%{params['tarjeta']}%")
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ''
    # Usar la tabla creada en config/db.py: historial_tarjetas
    sql = f"""
    SELECT
        ht.id,
        COALESCE(t.uid, ht.uid) AS uid_tarjeta,
        CASE LOWER(TRIM(ht.accion))
            WHEN 'creada' THEN 'alta'
            WHEN 'alta' THEN 'alta'
            WHEN 'activo' THEN 'alta'
            WHEN 'baja' THEN 'baja'
            WHEN 'inactivo' THEN 'baja'
            WHEN 'desactivado' THEN 'baja'
            WHEN 'editada' THEN 'editada'
            WHEN 'editado' THEN 'editada'
            WHEN 'edicion' THEN 'editada'
            WHEN 'modificada' THEN 'editada'
            WHEN 'eliminada' THEN 'eliminada'
            WHEN 'eliminado' THEN 'eliminada'
            WHEN 'sin cambio' THEN 'sin cambio'
            WHEN 'sincambio' THEN 'sin cambio'
            ELSE LOWER(ht.accion)
        END AS accion,
        COALESCE(ht.ejecutado_por, 'Sistema') AS responsable,
        ht.fecha_hora
    FROM historial_tarjetas ht
    LEFT JOIN tarjetas t ON t.id = ht.tarjeta_id OR t.uid = ht.uid
    {where}
    ORDER BY ht.fecha_hora DESC
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(sql, valores)
            rows = cursor.fetchall()
            # Normalize rows into dicts
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
            rows = norm_rows
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        return jsonify(rows)
    finally:
        connection.close()


@reportes_api.route('/api/reportes/enrolamiento_historial', methods=['GET'])
def enrolamiento_historial():
    params = request.args
    filtros = []
    valores = []
    if params.get('fecha_desde'):
        filtros.append('fecha_hora >= ?')
        valores.append(f"{params['fecha_desde']} 00:00:00")
    if params.get('fecha_hasta'):
        filtros.append('fecha_hora <= ?')
        valores.append(f"{params['fecha_hasta']} 23:59:59")
    if params.get('estado'):
        filtros.append('LOWER(TRIM(estado)) = ?')
        valores.append(params['estado'].strip().lower())
    elif params.get('accion'):
        filtros.append('LOWER(TRIM(estado)) = ?')
        valores.append(params['accion'].strip().lower())
    if params.get('responsable'):
        filtros.append('LOWER(responsable) LIKE ?')
        valores.append(f"%{params['responsable'].strip().lower()}%")
    if params.get('persona'):
        filtros.append('LOWER(nombre_persona) LIKE ?')
        valores.append(f"%{params['persona'].strip().lower()}%")
    if params.get('tarjeta'):
        filtros.append('(LOWER(tarjeta_uid) LIKE ? OR LOWER(tarjeta_pin) LIKE ?)')
        valores.append(f"%{params['tarjeta'].strip().lower()}%")
        valores.append(f"%{params['tarjeta'].strip().lower()}%")
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ''
    sql = f"""
    SELECT
        id,
        enrolar_id,
        persona_id,
        nombre_persona,
        perfil,
        tarjeta_uid,
        tarjeta_pin,
        estado,
        responsable,
        descripcion,
        fecha_hora
    FROM historial_enrolamiento
    {where}
    ORDER BY fecha_hora DESC
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(sql, valores)
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description] if cursor.description else []
            norm_rows = []
            for r in rows:
                try:
                    norm_rows.append(dict(r))
                except Exception:
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
            accesos_count = 0
            try:
                cursor.execute('SELECT COUNT(*) FROM registro_acceso')
                accesos_count = cursor.fetchone()[0]
            except Exception:
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
