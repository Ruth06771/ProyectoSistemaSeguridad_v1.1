from flask import Blueprint, request, make_response
from io import BytesIO
from config.db import get_connection
import os

# Optional import of reportlab (heavy dependency). If it's not available
# we keep the module importable and return a helpful 500 at runtime.
try:
    from reportlab.lib.pagesizes import letter
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

    # Construir consulta
    query = "SELECT * FROM accesos_personal WHERE 1=1"
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
                # convertir cada fila en dict usando los nombres de columna
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=80)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Reporte de Accesos Detallado', styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Construir matriz de datos para la tabla con encabezados fijos
    data = [[
        'ID', 'Fecha y Hora', 'Movimiento', 'Nombre', 'Documento', 'UID Tarjeta', 'Registrado Por', 'Descripción'
    ]]

    for row in registros:
        # row es dict por construcción
        data.append([
            row.get('id', ''),
            row.get('fecha_hora', ''),
            row.get('tipo_movimiento', row.get('movimiento', '')),
            row.get('nombre_completo', ''),
            row.get('documento_identidad', row.get('documento', '')),
            row.get('uid_tarjeta', ''),
            row.get('registrado_por', ''),
            row.get('descripcion', '')
        ])

    # Crear tabla
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
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
