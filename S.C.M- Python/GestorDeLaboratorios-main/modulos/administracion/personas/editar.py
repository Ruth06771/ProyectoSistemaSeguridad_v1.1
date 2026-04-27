from flask import Flask, request, redirect, session, url_for, flash
from flask import render_template_string
from config.db import get_connection
from pathlib import Path
import re

app = Flask(__name__)
app.secret_key = 'TU_SECRETO_AQUI'  # Cambiar por algo seguro

# Try to load an HTML template stored alongside this module (editar.html).
# Some legacy files store a python assignment `html_form = """..."""`.
html_form = None
try:
    tpl_path = Path(__file__).resolve().with_suffix('.html')
    if tpl_path.exists():
        raw = tpl_path.read_text(encoding='utf-8')
        m = re.search(r"html_form\s*=\s*(?:\"\"\"|\'\'\')([\s\S]*?)(?:\"\"\"|\'\'\')", raw)
        if m:
            html_form = m.group(1)
        else:
            # fallback: use entire file contents
            html_form = raw
except Exception:
    html_form = None

# Decorador para admin
def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'admin':
            return redirect(url_for('login', error="Acceso no autorizado"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    # Intentar conectar a la base de datos
    try:
        connection = get_connection()
    except Exception as e:
        flash("Error de conexión a la base de datos: " + str(e), "danger")
        return redirect(url_for('index'))

    cursor = None
    try:
        cursor = connection.cursor()

        # Procesar formulario POST
        if request.method == 'POST':
            nombre_completo = request.form.get('nombre_completo', '').strip()
            fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
            correo = request.form.get('correo', '').strip()
            telefono_personal = request.form.get('telefono_personal', '').strip()
            documento_identidad = request.form.get('documento_identidad', '').strip()
            sexo = request.form.get('sexo', '').strip()
            tipo_sangre = request.form.get('tipo_sangre', '').strip()
            persona_emergencia = request.form.get('persona_emergencia', '').strip()
            telefono_emergencia = request.form.get('telefono_emergencia', '').strip()

            # Validaciones básicas
            import re
            if not all([nombre_completo, fecha_nacimiento, correo, documento_identidad, sexo, persona_emergencia, telefono_emergencia]):
                flash("Los campos marcados como obligatorios son requeridos.", "danger")
                return redirect(url_for('editar', id=id))
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
                flash("Correo electrónico inválido.", "danger")
                return redirect(url_for('editar', id=id))
            
            if telefono_personal and not telefono_personal.isdigit():
                flash("El teléfono personal debe contener solo números.", "danger")
                return redirect(url_for('editar', id=id))
            
            if not telefono_emergencia.isdigit():
                flash("El teléfono de emergencia debe contener solo números.", "danger")
                return redirect(url_for('editar', id=id))

            # Actualizar registro
            sql_update = """
                UPDATE personas
                SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s, telefono_personal=%s,
                    documento_identidad=%s, sexo=%s, tipo_sangre=%s, persona_emergencia=%s, telefono_emergencia=%s
                WHERE id=%s
            """
            # sqlite uses ? placeholders; pymysql uses %s. Detect and adapt.
            if connection.__class__.__module__.startswith('sqlite3'):
                sql_update = sql_update.replace('%s', '?')

            cursor.execute(sql_update, (nombre_completo, fecha_nacimiento, correo, telefono_personal,
                                        documento_identidad, sexo, tipo_sangre, persona_emergencia, telefono_emergencia, id))
            connection.commit()
            flash("Datos actualizados correctamente.", "success")
            return redirect(url_for('index'))

        # Obtener datos actuales para mostrar en el formulario
        placeholder = '%s'
        params = (id,)
        if connection.__class__.__module__.startswith('sqlite3'):
            placeholder = '?'
        cursor.execute(f"SELECT * FROM personas WHERE id = {placeholder}", params)
        persona = cursor.fetchone()
        if persona and hasattr(persona, 'keys'):
            persona = dict(persona)
        if not persona:
            flash("Persona no encontrada.", "danger")
            return redirect(url_for('index'))

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        try:
            connection.close()
        except Exception:
            pass

 
#html 
    return render_template_string(html_form, persona=persona)

@app.route('/login')
def login():
    return "Página de login (implementar aquí)"

@app.route('/index')
def index():
    return "Página principal (lista de personas)"

if __name__ == "__main__":
    app.run(debug=True)
