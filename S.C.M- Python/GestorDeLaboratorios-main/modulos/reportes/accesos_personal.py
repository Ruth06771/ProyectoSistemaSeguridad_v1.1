from flask import Flask, render_template, request, redirect, url_for
from config.db import get_connection

app = Flask(__name__)

@app.route('/accesos_personal')
def accesos_personal():
    # Obtener filtros del query string
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    tipo_movimiento = request.args.get('tipo_movimiento', '')
    nombre_completo = request.args.get('nombre_completo', '')
    uid_tarjeta = request.args.get('uid_tarjeta', '')

    # Construir consulta dinámica
    query = "SELECT * FROM registro_accesos WHERE 1=1"
    params = []

    if fecha_desde:
        query += " AND fecha_hora >= %s"
        params.append(fecha_desde + " 00:00:00")
    if fecha_hasta:
        query += " AND fecha_hora <= %s"
        params.append(fecha_hasta + " 23:59:59")
    if tipo_movimiento:
        query += " AND tipo_movimiento = %s"
        params.append(tipo_movimiento)
    if nombre_completo:
        query += " AND nombre_completo LIKE %s"
        params.append(f"%{nombre_completo}%")
    if uid_tarjeta:
        query += " AND uid_tarjeta LIKE %s"
        params.append(f"%{uid_tarjeta}%")

    query += " ORDER BY fecha_hora DESC"

    # Conectar a la base de datos
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
        nombre_completo=nombre_completo,
        uid_tarjeta=uid_tarjeta
    )

if __name__ == '__main__':
    app.run(debug=True)
