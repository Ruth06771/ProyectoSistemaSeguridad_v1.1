from flask import Flask, request, send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from io import BytesIO
from config.db import get_connection

app = Flask(__name__)

@app.route('/exportar_excel_tarjetas')
def exportar_excel_tarjetas():
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    tipo_accion = request.args.get('tipo_accion', '')
    usuario_responsable = request.args.get('usuario_responsable', '')
    tarjeta = request.args.get('tarjeta', '')

    query = "SELECT * FROM historial_accesos WHERE 1=1"
    params = []

    if fecha_desde:
        query += " AND fecha_hora >= %s"
        params.append(f"{fecha_desde} 00:00:00")
    if fecha_hasta:
        query += " AND fecha_hora <= %s"
        params.append(f"{fecha_hasta} 23:59:59")
    if tipo_accion:
        query += " AND accion = %s"
        params.append(tipo_accion)
    if usuario_responsable:
        query += " AND usuario_responsable LIKE %s"
        params.append(f"%{usuario_responsable}%")
    if tarjeta:
        query += " AND tarjeta LIKE %s"
        params.append(f"%{tarjeta}%")

    query += " ORDER BY fecha_hora DESC"

    # Conectar a la base de datos y ejecutar consulta
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

    # Crear Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Accesos"

    # Encabezados
    encabezados = ['ID', 'Fecha y Hora', 'Acción', 'Usuario Responsable', 'Tarjeta RFID', 'Descripción']
    ws.append(encabezados)

    # Estilo de encabezado: negrita + fondo gris
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    for col_num, cell in enumerate(ws[1], 1):
        cell.font = header_font
        cell.fill = header_fill

    # Datos
    for row in resultados:
        ws.append([
            row['id'],
            row['fecha_hora'],
            row['accion'],
            row['usuario_responsable'],
            row['tarjeta'],
            row['descripcion']
        ])

    # Autoajustar ancho de columnas
    for column in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in column)
        column_letter = column[0].column_letter
        ws.column_dimensions[column_letter].width = max_length + 2

    # Guardar en un buffer para enviar como descarga
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name="reporte_accesos.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    app.run(debug=True)
