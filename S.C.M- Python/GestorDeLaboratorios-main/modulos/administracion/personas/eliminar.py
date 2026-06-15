from flask import Flask, request, redirect, session, url_for, flash
from config.db import get_connection

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro


# Ruta para eliminar persona
@app.route("/personas/eliminar", methods=["POST"])
def eliminar_persona():
    # Verificar sesión de admin
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect(url_for("login", error="Acceso no autorizado"))

    # Obtener ID
    try:
        persona_id = int(request.form.get("id", 0))
    except ValueError:
        persona_id = 0

    if persona_id <= 0:
        flash("ID inválido para eliminación.", "error")
        return redirect(url_for("index"))

    # Conectar a la base de datos
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # adapt placeholder for sqlite vs mysql
        placeholder = '%s'
        params = (persona_id,)
        if conn.__class__.__module__.startswith('sqlite3'):
            placeholder = '?'
        # Borrado lógico
        cursor.execute(f"UPDATE personas SET estado = 0 WHERE id = {placeholder}", params)
        conn.commit()

        flash("Registro eliminado correctamente.", "success")
    except Exception as e:
        # generic error handling so sqlite or mysql exceptions are caught
        flash(f"Error al eliminar el registro: {str(e)}", "error")
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass

    return redirect(url_for("index"))


