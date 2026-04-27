from flask import Blueprint, request, jsonify
from config.db import get_connection

bitacora_api = Blueprint('bitacora_api', __name__)

@bitacora_api.route('/api/bitacora', methods=['GET'])
def listar_bitacora():
    params = []
    where = 'WHERE 1=1'
    q_modulo = request.args.get('modulo')
    q_accion = request.args.get('accion')
    q_usuario = request.args.get('usuario')
    if q_modulo:
        where += ' AND modulo = %s'
        params.append(q_modulo)
    if q_accion:
        where += ' AND accion = %s'
        params.append(q_accion)
    if q_usuario:
        where += ' AND usuario = %s'
        params.append(q_usuario)
    limit = request.args.get('limit', type=int) or 100

    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            sql = f"SELECT * FROM historial_acciones {where} ORDER BY fecha_hora DESC LIMIT %s"
            params_with_limit = params + [limit]
            if conn.__class__.__module__.startswith('sqlite3'):
                sql = sql.replace('%s', '?')
            cur.execute(sql, params_with_limit)
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                out = [dict(r) for r in rows]
            else:
                out = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(out)
    finally:
        conn.close()
