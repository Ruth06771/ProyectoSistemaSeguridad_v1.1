from flask import Flask, request, send_file
from config.db import get_connection
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)

@app.route('/exportar_excel_tarjetas')
def exportar_excel_tarjetas():
    # Capturar filtros
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    accion = request.args.get('accion', '')
    usuario = request.args.get('usuario', '')
    tarjeta = request.args.get('tarjeta', '')

    # Construir consulta dinámica
    query = "SELECT * FROM historial_tarjetas WHERE 1=1"
    params = []

    if fecha_desde:
        query += " AND ejecutado_en >= %s"
        params.append(fecha_desde + " 00:00:00")
    if fecha_hasta:
        query += " AND ejecutado_en <= %s"
        params.append(fecha_hasta + " 23:59:59")
    if accion:
        query += " AND accion = %s"
        params.append(accion)
    if usuario:
        query += " AND ejecutado_por LIKE %s"
        params.append(f"%{usuario}%")
    if tarjeta:
        query += " AND UID LIKE %s"
        params.append(f"%{tarjeta}%")

    query += " ORDER BY ejecutado_en DESC"

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

    # Crear archivo Excel en memoria
    wb = Workbook()
    ws = wb.active
    ws.title = "Historial Tarjetas"

    # Encabezados
    headers = ['ID', 'UID Tarjeta', 'Nombre Completo', 'Acción', 'Ejecutado Por', 'Fecha y Hora']
    ws.append(headers)

    # Rellenar filas
    for row in registros:
        ws.append([
            row['id'],
            row['uid'],
            row['nombre_completo'],
            row['accion'],
            row['ejecutado_por'],
            row['ejecutado_en']
        ])

    # Autoajustar ancho de columnas
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[column_letter].width = max_length + 2

    # Guardar en un buffer y enviar
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        download_name="historial_altas_bajas_tarjetas.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    app.run(debug=True)
