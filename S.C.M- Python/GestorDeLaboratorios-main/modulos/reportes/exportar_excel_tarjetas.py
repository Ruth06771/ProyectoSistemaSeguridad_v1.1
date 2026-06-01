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

    # Construir consulta dinámica para el historial de tarjetas
    query = """
    SELECT
        ht.id,
        COALESCE(t.uid, ht.uid) AS tarjeta_uid,
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
            ELSE NULL
        END AS accion,
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
        accion_valor = accion.strip().lower()
        if accion_valor in ('alta', 'creada', 'activo'):
            query += " AND LOWER(TRIM(ht.accion)) IN ('alta', 'creada', 'activo')"
        elif accion_valor in ('baja', 'inactivo', 'desactivado'):
            query += " AND LOWER(TRIM(ht.accion)) IN ('baja', 'inactivo', 'desactivado')"
        elif accion_valor in ('editada', 'editado', 'edicion', 'modificada'):
            query += " AND LOWER(TRIM(ht.accion)) IN ('editada', 'editado', 'edicion', 'modificada')"
        elif accion_valor in ('eliminada', 'eliminado'):
            query += " AND LOWER(TRIM(ht.accion)) IN ('eliminada', 'eliminado')"
        else:
            query += " AND 1=0"
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
    headers = ['ID', 'UID Tarjeta', 'Acción', 'Responsable', 'Fecha y Hora']
    ws.append(headers)

    # Rellenar filas
    for row in registros:
        ws.append([
            row.get('id'),
            row.get('tarjeta_uid') or row.get('uid'),
            row.get('accion'),
            row.get('responsable'),
            row.get('fecha_hora')
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
