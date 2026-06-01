from flask import Blueprint, request, make_response
from io import BytesIO
from config.db import get_connection
import os

# Optional import of reportlab (heavy dependency). If it's not available
# we keep the module importable and return a helpful 500 at runtime.
try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

bp = Blueprint('exportar_pdf_personal', __name__)


@bp.route('/reporte_accesos_personal')
def reporte_accesos_personal():
    if not REPORTLAB_AVAILABLE:
        return make_response('ReportLab is not installed. Install it with: pip install reportlab', 500)

    # Obtener filtros
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    tipo_movimiento = request.args.get('tipo_movimiento', '')
    nombre_completo = request.args.get('nombre_completo', '')
    uid_tarjeta = request.args.get('uid_tarjeta', '')
    resultado = request.args.get('resultado', '')
    credencial = request.args.get('credencial', '')

    # Construir consulta
    query = '''
    SELECT
        ra.id,
        ra.fecha_hora,
        COALESCE(p.nombre_completo, 'Desconocido') AS persona,
        CASE
            WHEN LOWER(TRIM(tm.movimiento)) = 'entrada' THEN 'Entrada'
            WHEN LOWER(TRIM(tm.movimiento)) = 'salida' THEN 'Salida'
            WHEN LOWER(ra.descripcion) LIKE '%retirar%' THEN 'Entrada'
            WHEN LOWER(ra.descripcion) LIKE '%devolver%' THEN 'Salida'
            ELSE COALESCE(tm.movimiento, ra.descripcion, 'Desconocido')
        END AS movimiento,
        ra.resultado,
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
    if nombre_completo:
        query += " AND p.nombre_completo LIKE %s"
        params.append(f"%{nombre_completo}%")
    if uid_tarjeta:
        query += " AND ra.tarjeta_uid LIKE %s"
        params.append(f"%{uid_tarjeta}%")
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
    query += " ORDER BY ra.fecha_hora DESC"

    # Ejecutar consulta y transformar resultados en lista de diccionarios
    connection = get_connection()
    registros = []
    try:
        cursor = connection.cursor()
        try:
            exec_query = query
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_query = exec_query.replace('%s', '?')
            cursor.execute(exec_query, params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            fetched = cursor.fetchall()
            if fetched:
                registros = [dict(zip(cols, row)) for row in fetched]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

    # Preparar PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=40,
        bottomMargin=40,
        leftMargin=20,
        rightMargin=20
    )
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Historial de Accesos', styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Crear estilo para celdas con envolvimiento de texto
    cell_style = getSampleStyleSheet()['Normal']
    cell_style.fontSize = 7
    cell_style.leading = 8

    # Construir matriz de datos para la tabla con encabezados fijos y Paragraph objects
    headers = ['ID', 'Fecha y Hora', 'Persona', 'Movimiento', 'Acción ESP', 'Resultado', 'Credencial', 'UID Tarjeta', 'Descripción']
    data = [[Paragraph(str(h), cell_style) for h in headers]]

    for row in registros:
        data.append([
            Paragraph(str(row.get('id', '')), cell_style),
            Paragraph(str(row.get('fecha_hora', '')), cell_style),
            Paragraph(str(row.get('persona', '')), cell_style),
            Paragraph(str(row.get('movimiento', '')), cell_style),
            Paragraph(str(row.get('accion', '')), cell_style),
            Paragraph(str(row.get('resultado', '')), cell_style),
            Paragraph(str(row.get('credencial', '')), cell_style),
            Paragraph(str(row.get('tarjeta_uid', '')), cell_style),
            Paragraph(str(row.get('descripcion', '')), cell_style)
        ])

    # Crear tabla con anchos de columna aproximados para ajuste horizontal
    column_widths = [30, 65, 85, 55, 60, 55, 55, 70, 130]
    table = Table(data, repeatRows=1, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
    ]))
    elements.append(table)

    # Función para añadir header con logo en cada página
    def add_header(canvas, doc):
        canvas.saveState()
        # Dibujar dos logos: UEB a la izquierda, TechSpot a la derecha (fallbacks si faltan)
        base = os.path.join(os.path.dirname(__file__), '../../static/img')
        left_candidates = ['ueb-logo.png', 'uebLogo.png', 'ueb-logo.jpg', 'uebLogo.png.jpg', 'ueb-logo.jpeg']
        left_logo = None
        for name in left_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                left_logo = p
                break
        right_candidates = ['techspot-logo.png', 'techspot.png']
        right_logo = None
        for name in right_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                right_logo = p
                break
        if not right_logo:
            right_logo = left_logo
        if not left_logo:
            left_logo = right_logo
        try:
            if left_logo and os.path.exists(left_logo):
                canvas.drawImage(left_logo, 30, 700, width=60, height=60, preserveAspectRatio=True)
            if right_logo and os.path.exists(right_logo):
                canvas.drawImage(right_logo, 520, 700, width=60, height=60, preserveAspectRatio=True)
        except Exception as e:
            print(f"Error al dibujar logos en personal: {e}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)
    pdf = buffer.getvalue()
    buffer.close()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_accesos_personal.pdf'
    return response


@bp.route('/reporte_enrolamiento')
def reporte_enrolamiento():
    if not REPORTLAB_AVAILABLE:
        return make_response('ReportLab is not installed. Install it with: pip install reportlab', 500)

    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    accion = request.args.get('accion', '')
    responsable = request.args.get('responsable', '')
    persona = request.args.get('persona', '')
    tarjeta = request.args.get('tarjeta', '')

    query = '''
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
    WHERE 1=1
    '''
    params = []
    if fecha_desde:
        query += " AND fecha_hora >= %s"
        params.append(fecha_desde + " 00:00:00")
    if fecha_hasta:
        query += " AND fecha_hora <= %s"
        params.append(fecha_hasta + " 23:59:59")
    if accion:
        query += " AND LOWER(TRIM(estado)) = %s"
        params.append(accion.strip().lower())
    if responsable:
        query += " AND LOWER(responsable) LIKE %s"
        params.append(f"%{responsable.strip().lower()}%")
    if persona:
        query += " AND LOWER(nombre_persona) LIKE %s"
        params.append(f"%{persona.strip().lower()}%")
    if tarjeta:
        query += " AND (LOWER(tarjeta_uid) LIKE %s OR LOWER(tarjeta_pin) LIKE %s)"
        params.append(f"%{tarjeta.strip().lower()}%")
        params.append(f"%{tarjeta.strip().lower()}%")
    query += " ORDER BY fecha_hora DESC"

    connection = get_connection()
    registros = []
    try:
        cursor = connection.cursor()
        try:
            exec_query = query
            if connection.__class__.__module__.startswith('sqlite3'):
                exec_query = exec_query.replace('%s', '?')
            cursor.execute(exec_query, params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            fetched = cursor.fetchall()
            if fetched:
                registros = [dict(zip(cols, row)) for row in fetched]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=40,
        bottomMargin=40,
        leftMargin=20,
        rightMargin=20
    )
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Historial de Enrolamiento', styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Crear estilo para celdas con envolvimiento de texto
    cell_style = getSampleStyleSheet()['Normal']
    cell_style.fontSize = 6
    cell_style.leading = 7

    # Construir matriz de datos para la tabla con encabezados fijos y Paragraph objects
    headers = ['ID', 'Enrolar ID', 'Persona', 'Perfil', 'Tarjeta UID', 'PIN', 'Estado', 'Responsable', 'Descripción', 'Fecha y Hora']
    data = [[Paragraph(str(h), cell_style) for h in headers]]

    for row in registros:
        data.append([
            Paragraph(str(row.get('id', '')), cell_style),
            Paragraph(str(row.get('enrolar_id', '')), cell_style),
            Paragraph(str(row.get('nombre_persona', '')), cell_style),
            Paragraph(str(row.get('perfil', '')), cell_style),
            Paragraph(str(row.get('tarjeta_uid', '')), cell_style),
            Paragraph(str(row.get('tarjeta_pin', '')), cell_style),
            Paragraph(str(row.get('estado', '')), cell_style),
            Paragraph(str(row.get('responsable', '')), cell_style),
            Paragraph(str(row.get('descripcion', '')), cell_style),
            Paragraph(str(row.get('fecha_hora', '')), cell_style)
        ])

    column_widths = [25, 45, 85, 50, 60, 40, 50, 70, 120, 90]
    table = Table(data, repeatRows=1, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1)
    ]))
    elements.append(table)

    def add_header(canvas, doc):
        canvas.saveState()
        base = os.path.join(os.path.dirname(__file__), '../../static/img')
        left_candidates = ['ueb-logo.png', 'uebLogo.png', 'ueb-logo.jpg', 'ueb-logo.jpeg']
        left_logo = None
        for name in left_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                left_logo = p
                break
        right_candidates = ['techspot-logo.png', 'techspot.png']
        right_logo = None
        for name in right_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                right_logo = p
                break
        if not right_logo:
            right_logo = left_logo
        if not left_logo:
            left_logo = right_logo
        try:
            if left_logo and os.path.exists(left_logo):
                canvas.drawImage(left_logo, 30, 700, width=60, height=60, preserveAspectRatio=True)
            if right_logo and os.path.exists(right_logo):
                canvas.drawImage(right_logo, 520, 700, width=60, height=60, preserveAspectRatio=True)
        except Exception as e:
            print(f"Error al dibujar logos en enrolamiento: {e}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)
    pdf = buffer.getvalue()
    buffer.close()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_enrolamiento.pdf'
    return response
