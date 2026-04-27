from flask import Flask, render_template_string, request, redirect, url_for
from config.db import get_connection
from pathlib import Path
import re

app = Flask(__name__)
app.secret_key = 'TU_SECRETO_AQUI'

# Try to load an HTML template in the same folder (index.html or index.tpl)
template = None
try:
    tpl_path = Path(__file__).resolve().with_suffix('.html')
    if tpl_path.exists():
        template = tpl_path.read_text(encoding='utf-8')
    else:
        # look for .tpl
        tpl2 = tpl_path.with_suffix('.tpl')
        if tpl2.exists():
            template = tpl2.read_text(encoding='utf-8')
except Exception:
    template = None


# Página principal: listado y búsqueda
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = None
    cursor = None
    try:
        conn = get_connection()

        if request.method == 'POST':
            # Actualizar estado de tarjeta
            tarjeta_id = request.form.get('id')
            nuevo_estado = request.form.get('estado')
            cursor = conn.cursor()
            try:
                placeholder = '%s'
                if conn.__class__.__module__.startswith('sqlite3'):
                    placeholder = '?'
                cursor.execute(f"UPDATE tarjetas SET estado={placeholder} WHERE id={placeholder}", (nuevo_estado, tarjeta_id))
                conn.commit()
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
            return redirect(url_for('index'))

        # Manejo de búsqueda
        busqueda = request.args.get('buscar', '').strip()
        param = f"%{busqueda}%"

        cursor = conn.cursor()
        try:
            if busqueda:
                sql = """
                SELECT * FROM tarjetas
                WHERE uid LIKE %s OR nombre_completo LIKE %s OR correo LIKE %s
                ORDER BY creada_en DESC
                """
                if conn.__class__.__module__.startswith('sqlite3'):
                    sql = sql.replace('%s', '?')
                cursor.execute(sql, (param, param, param))
            else:
                sql = "SELECT * FROM tarjetas ORDER BY creada_en DESC"
                cursor.execute(sql)

            tarjetas = cursor.fetchall()
            # normalize sqlite rows to dicts
            if tarjetas and hasattr(tarjetas[0], 'keys'):
                tarjetas = [dict(r) for r in tarjetas]
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    if template:
        return render_template_string(template, tarjetas=tarjetas, busqueda=busqueda)
    # Fallback simple rendering if template not present
    rows_html = ''.join(f"<li>{t.get('nombre_completo','')} - {t.get('uid','')}</li>" for t in (tarjetas or []))
    return f"<h3>Tarjetas</h3><form method='get'><input name='buscar' value='{busqueda}'/><button>Buscar</button></form><ul>{rows_html}</ul>"

if __name__ == '__main__':
    app.run(debug=True)
