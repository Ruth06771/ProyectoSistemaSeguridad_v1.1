from flask import Flask, request, render_template
from urllib.parse import urlencode
from config.db import get_connection

app = Flask(__name__)

@app.route('/historial_tarjetas')
def historial_tarjetas():
    # Capturar filtros
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    accion = request.args.get('accion', '')
    usuario = request.args.get('usuario', '')
    tarjeta = request.args.get('tarjeta', '')

    # Construir query dinámico
    query = """
    SELECT
        ht.id,
        COALESCE(t.uid, ht.uid) AS tarjeta_uid,
        ht.accion,
        ht.ejecutado_por AS responsable,
        ht.fecha_hora
    FROM historial_tarjetas ht
    LEFT JOIN tarjetas t ON t.id = ht.tarjeta_id OR t.uid = ht.uid
    WHERE 1=1
    """
    params = []

    if fecha_desde:
        query += " AND ht.fecha_hora >= %s"
        params.append(fecha_desde + " 00:00:00")
    if fecha_hasta:
        query += " AND ht.fecha_hora <= %s"
        params.append(fecha_hasta + " 23:59:59")
    if accion:
        query += " AND ht.accion = %s"
        params.append(accion)
    if usuario:
        query += " AND ht.ejecutado_por LIKE %s"
        params.append(f"%{usuario}%")
    if tarjeta:
        query += " AND (ht.uid LIKE %s OR t.uid LIKE %s)"
        params.append(f"%{tarjeta}%")
        params.append(f"%{tarjeta}%")

    query += " ORDER BY ht.fecha_hora DESC"

    # Ejecutar consulta
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            exec_query = query
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_query = exec_query.replace('%s', '?')
            cursor.execute(exec_query, params)
            resultados = cursor.fetchall()
            if resultados and hasattr(resultados[0], 'keys'):
                resultados = [dict(r) for r in resultados]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

    # Construir query string para exportar
    query_string = urlencode(request.args)

    return render_template('historial_tarjetas.html',
                           resultados=resultados,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           accion=accion,
                           usuario=usuario,
                           tarjeta=tarjeta,
                           query_string=query_string)

if __name__ == "__main__":
    app.run(debug=True)
