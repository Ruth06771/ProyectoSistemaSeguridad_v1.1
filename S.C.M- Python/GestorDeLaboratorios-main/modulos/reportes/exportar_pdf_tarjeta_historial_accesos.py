from flask import Blueprint, request, render_template, make_response
from config.db import get_connection

# Optional weasyprint import (heavy dependency). Keep module importable
# and return helpful error if library missing at runtime.
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

import os


bp = Blueprint('exportar_pdf_tarjeta_historial_accesos', __name__)


@bp.route('/reporte_tarjetas')
def reporte_tarjetas():
    if not WEASYPRINT_AVAILABLE:
        return make_response('WeasyPrint is not installed.', 500)

    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    accion = request.args.get('accion')
    usuario = request.args.get('usuario')
    tarjeta = request.args.get('tarjeta')

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
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

            exec_query = query
            if conn.__class__.__module__.startswith('sqlite3'):
                exec_query = exec_query.replace('%s', '?')

            cursor.execute(exec_query, params)
            rows = cursor.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                rows = [dict(r) for r in rows]
        finally:
            try: cursor.close()
            except: pass
    finally:
        conn.close()

    # rutas absolutas para WeasyPrint
    from flask import current_app
    static_img_dir = os.path.join(current_app.root_path, 'static', 'img').replace('\\','/')

    left_logo = 'ueb-logo.png'
    right_logo = 'techspot-logo.png'

    html_out = render_template('reporte_tarjetas.html', 
                               rows=rows,
                               static_img_path=static_img_dir,
                               left_logo=left_logo,
                               right_logo=right_logo)

    pdf = HTML(string=html_out).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_tarjetas.pdf'
    return response
