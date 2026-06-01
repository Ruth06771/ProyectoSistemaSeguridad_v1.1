from flask import Flask, render_template, request, redirect, url_for
from config.db import get_connection

app = Flask(__name__)

@app.route('/accesos_personal')
def accesos_personal():
    # Obtener filtros del query string
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    tipo_movimiento = request.args.get('tipo_movimiento', '')
    resultado = request.args.get('resultado', '')
    credencial = request.args.get('credencial', '')
    nombre_completo = request.args.get('nombre_completo', '')
    uid_tarjeta = request.args.get('uid_tarjeta', '')

    query = '''
    SELECT
        ra.id,
        ra.fecha_hora,
        COALESCE(p.nombre_completo, 'Desconocido') AS nombre_completo,
        tm.movimiento AS tipo_movimiento,
        ra.resultado,
        CASE
            WHEN LOWER(TRIM(COALESCE(ra.credencial, 'Tarjeta'))) IN ('uid', 'tarjeta') THEN 'TARJETA'
            WHEN LOWER(TRIM(ra.credencial)) = 'pin' THEN 'PIN'
            ELSE UPPER(ra.credencial)
        END AS credencial,
        ra.tarjeta_uid,
        ra.descripcion
    FROM registro_acceso ra
    LEFT JOIN enrolar e ON ra.enrolar_id = e.id
    LEFT JOIN personas p ON e.persona_id = p.id
    LEFT JOIN tipo_movimiento tm ON ra.tipo_movimiento_id = tm.id
    WHERE 1=1
    '''
    params = []

    if fecha_desde:
        query += " AND ra.fecha_hora >= %s"
        params.append(fecha_desde + " 00:00:00")
    if fecha_hasta:
        query += " AND ra.fecha_hora <= %s"
        params.append(fecha_hasta + " 23:59:59")
    if tipo_movimiento:
        query += " AND LOWER(TRIM(tm.movimiento)) = %s"
        params.append(tipo_movimiento.strip().lower())
    if resultado:
        query += " AND ra.resultado = %s"
        params.append(resultado)
    if credencial:
        credencial_val = credencial.strip().lower()
        if credencial_val == 'tarjeta':
            query += " AND LOWER(TRIM(ra.credencial)) IN ('tarjeta', 'uid')"
        elif credencial_val == 'pin':
            query += " AND LOWER(TRIM(ra.credencial)) = 'pin'"
        else:
            query += " AND LOWER(TRIM(ra.credencial)) = %s"
            params.append(credencial_val)
    if nombre_completo:
        query += " AND p.nombre_completo LIKE %s"
        params.append(f"%{nombre_completo}%")
    if uid_tarjeta:
        query += " AND ra.tarjeta_uid LIKE %s"
        params.append(f"%{uid_tarjeta}%")

    query += " ORDER BY ra.fecha_hora DESC"

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            exec_query = query
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_query = exec_query.replace('%s', '?')
            cursor.execute(exec_query, params)
            registros = cursor.fetchall()
            if registros and hasattr(registros[0], 'keys'):
                registros = [dict(r) for r in registros]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

    return render_template(
        'accesos_personal.html',
        registros=registros,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo_movimiento=tipo_movimiento,
        resultado=resultado,
        credencial=credencial,
        nombre_completo=nombre_completo,
        uid_tarjeta=uid_tarjeta
    )

if __name__ == '__main__':
    app.run(debug=True)
