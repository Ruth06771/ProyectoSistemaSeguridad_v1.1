from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)
app.secret_key = "TU_SECRETO"   # si usarás sesiones

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_base",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/reportes/tarjetas_historial")
def tarjetas_historial():
    # Filtros desde GET
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    tipo_accion = request.args.get("tipo_accion", "")
    accion = request.args.get("accion", "")
    usuario_responsable = request.args.get("usuario_responsable", "")
    tarjeta = request.args.get("tarjeta", "")

    query = "SELECT * FROM historial_accesos WHERE 1=1"
    params = []

    if fecha_desde:
        query += " AND fecha_hora >= %s"
        params.append(f"{fecha_desde} 00:00:00")
    if fecha_hasta:
        query += " AND fecha_hora <= %s"
        params.append(f"{fecha_hasta} 23:59:59")
    if tipo_accion:
        query += " AND tipo_accion = %s"
        params.append(tipo_accion)
    if accion:
        query += " AND accion = %s"
        params.append(accion)
    if usuario_responsable:
        query += " AND usuario_responsable LIKE %s"
        params.append(f"%{usuario_responsable}%")
    if tarjeta:
        query += " AND tarjeta LIKE %s"
        params.append(f"%{tarjeta}%")

    query += " ORDER BY fecha_hora DESC"

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        registros = cursor.fetchall()
    conn.close()

    return render_template("tarjetas_historial.html",
                           registros=registros,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           tipo_accion=tipo_accion,
                           accion=accion,
                           usuario_responsable=usuario_responsable,
                           tarjeta=tarjeta)

if __name__ == "__main__":
    app.run(debug=True)
