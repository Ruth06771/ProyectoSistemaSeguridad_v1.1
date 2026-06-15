from flask import Flask, render_template, request, redirect, url_for, session, flash
from config.db import get_connection

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro

# Ruta para listar personas y búsqueda
@app.route('/personas', methods=['GET'])
def personas_index():
    if 'usuario' not in session or session.get('rol') != 'admin':
        return redirect(url_for('login', error="Acceso no autorizado"))

    buscar = request.args.get('buscar', '').strip()
    personas = []

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            if buscar:
                param = f"%{buscar}%"
                # choose placeholder depending on driver
                placeholder = '%s'
                if conn.__class__.__module__.startswith('sqlite3'):
                    placeholder = '?'
                sql = f"""
                SELECT * FROM personas
                WHERE estado = 1 AND (nombre_completo LIKE {placeholder}
                OR documento_identidad LIKE {placeholder}
                OR correo LIKE {placeholder})
                ORDER BY nombre_completo ASC
                """
                cursor.execute(sql, (param, param, param))
            else:
                cursor.execute("SELECT * FROM personas WHERE estado = 1 ORDER BY nombre_completo ASC")

            personas = cursor.fetchall()
            # normalize sqlite rows to dicts when needed
            if personas and hasattr(personas[0], 'keys'):
                personas = [dict(r) for r in personas]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        conn.close()

    return render_template("personas.html", personas=personas, buscar=buscar)

# Ruta para eliminar persona
@app.route('/personas/eliminar', methods=['POST'])
def eliminar_persona():
    if 'usuario' not in session or session.get('rol') != 'admin':
        return redirect(url_for('login', error="Acceso no autorizado"))

    persona_id = request.form.get('id')
    if not persona_id:
        flash("ID inválido para eliminación.", "error")
        return redirect(url_for('personas_index'))

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            placeholder = '%s'
            params = (int(persona_id),)
            if conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            # Borrado lógico
            cursor.execute(f"UPDATE personas SET estado = 0 WHERE id={placeholder}", params)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        conn.commit()
        flash("Persona eliminada correctamente.", "success")
    finally:
        conn.close()

    return redirect(url_for('personas_index'))

