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

    # Construir consulta dinámica y unir datos de tarjeta/enrolamiento
    query = """
    SELECT
        ht.id,
        COALESCE(ht.nombre_completo, '') AS nombre_completo,
        ht.uid AS uid_tarjeta,
        t.pin AS pin,
        COALESCE(
            (SELECT pa.nombre
             FROM perfil_acceso_lab pa
             WHERE pa.id = (
                 SELECT e.perfil_acceso_lab_id
                 FROM enrolar e
                 WHERE (e.tarjeta_id = ht.tarjeta_id OR e.tarjeta_uid = ht.uid)
                   AND e.perfil_acceso_lab_id IS NOT NULL
                 ORDER BY e.fecha_de_registro DESC
                 LIMIT 1
             )
            ),
            ''
        ) AS perfil,
        COALESCE(
            (SELECT e.estado
             FROM enrolar e
             WHERE (e.tarjeta_id = ht.tarjeta_id OR e.tarjeta_uid = ht.uid)
             ORDER BY e.fecha_de_registro DESC
             LIMIT 1
            ),
            t.estado
        ) AS estado,
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
        query += " AND ht.uid LIKE %s"
        params.append(f"%{tarjeta}%")

    query += " ORDER BY ht.fecha_hora DESC"

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
    headers = ['ID', 'Nombre de la Persona', 'Tarjeta', 'PIN', 'Perfil', 'Fecha y Hora', 'Responsable', 'Estado']
    ws.append(headers)

    # Rellenar filas
    for row in registros:
        ws.append([
            row.get('id'),
            row.get('nombre_completo'),
            row.get('uid_tarjeta') or row.get('uid'),
            row.get('pin'),
            row.get('perfil'),
            row.get('fecha_hora'),
            row.get('responsable'),
            row.get('estado')
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
