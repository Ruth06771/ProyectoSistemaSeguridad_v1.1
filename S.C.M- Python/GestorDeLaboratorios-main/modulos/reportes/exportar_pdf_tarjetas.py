from flask import Blueprint, request, make_response
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

from config.db import get_connection
import os

bp = Blueprint('exportar_pdf_tarjetas', __name__)


@bp.route('/reporte_tarjetas')
def reporte_tarjetas():
    if not REPORTLAB_AVAILABLE:
        return ("ReportLab no está instalado en el servidor. Instale 'reportlab' para habilitar exportes PDF."), 500
    # Obtener filtros
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    persona = request.args.get('persona', '')
    accion = request.args.get('accion', '')
    usuario = request.args.get('usuario', '')
    tarjeta = request.args.get('tarjeta', '')

    # Construir consulta
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
    if persona:
        query += " AND ht.nombre_completo LIKE %s"
        params.append(f"%{persona}%")
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

    # Conectar y ejecutar consulta
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

    # Crear PDF con orientación landscape
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=80)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Historial de Registro de Tarjetas", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Construir tabla de datos
    data = [['ID', 'UID Tarjeta', 'Acción', 'Responsable', 'Fecha y Hora']]
    for row in resultados:
        data.append([
            str(row.get('id') or ''),
            str(row.get('tarjeta_uid') or row.get('uid') or ''),
            str(row.get('accion') or ''),
            str(row.get('responsable') or ''),
            str(row.get('fecha_hora') or '')
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    elements.append(table)

    # Función para añadir header con logo en cada página
    def add_header(canvas, doc):
        canvas.saveState()
        # Dibujar dos logos: UEB a la izquierda, TechSpot a la derecha (fallbacks si faltan)
        base = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'img')
        # Buscar variantes del logo UEB
        left_candidates = ['ueb-logo.png', 'uebLogo.png', 'ueb-logo.jpg', 'uebLogo.png.jpg', 'ueb-logo.jpeg']
        left_logo = None
        for name in left_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                left_logo = p
                left_name = name
                break
        # Techspot logo (right)
        right_candidates = ['techspot-logo.png', 'techspot.png']
        right_logo = None
        for name in right_candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                right_logo = p
                right_name = name
                break
        # Fallback behavior
        if not right_logo:
            right_logo = left_logo
        if not left_logo:
            left_logo = right_logo
        # Dibujar si existen
        try:
            if left_logo and os.path.exists(left_logo):
                canvas.drawImage(left_logo, 30, 700, width=60, height=60, preserveAspectRatio=True)
            if right_logo and os.path.exists(right_logo):
                canvas.drawImage(right_logo, 520, 700, width=60, height=60, preserveAspectRatio=True)
        except Exception as e:
            print(f"Error al dibujar logos en tarjetas: {e}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)
    pdf = buffer.getvalue()
    buffer.close()

    # Responder PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_tarjetas.pdf'
    return response
