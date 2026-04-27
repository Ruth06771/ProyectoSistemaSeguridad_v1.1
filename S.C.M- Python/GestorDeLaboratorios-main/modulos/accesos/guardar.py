from flask import Flask, request, redirect, session, flash, url_for
from config.db import get_connection

app = Flask(__name__)
app.secret_key = 'TU_SECRETO_AQUI'  # Cambiar por algo seguro


@app.route('/registrar_tarjeta', methods=['POST'])
def registrar_tarjeta():
    # Verificar autenticación y rol
    if 'usuario' not in session or session.get('rol') != 'admin':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))  # Ajusta según tu ruta de login

    # Obtener y limpiar datos del formulario
    uid = request.form.get('uid', '').strip()
    nombre_completo = request.form.get('nombre_completo', '').strip()
    correo = request.form.get('correo', '').strip()

    # Validación básica
    if not uid or not nombre_completo or not correo:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('nueva_tarjeta'))  # Ajusta según tu ruta

    # Conectar a la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # adapt placeholder for sqlite vs mysql
        placeholder = '%s'
        params = (uid,)
        if conn.__class__.__module__.startswith('sqlite3'):
            placeholder = '?'
        cursor.execute(f"SELECT id FROM tarjetas WHERE uid={placeholder}", params)
        if cursor.fetchone():
            flash("El UID ya está registrado.", "danger")
            return redirect(url_for('nueva_tarjeta'))

        # Insertar nueva tarjeta
        sql = "INSERT INTO tarjetas (uid, nombre_completo, correo) VALUES (%s, %s, %s)"
        if conn.__class__.__module__.startswith('sqlite3'):
            sql = sql.replace('%s', '?')
        cursor.execute(sql, (uid, nombre_completo, correo))
        conn.commit()
        flash("Tarjeta registrada correctamente.", "success")
        return redirect(url_for('index'))
    except Exception as e:
        conn.rollback()
        flash(f"Error al guardar la tarjeta: {str(e)}", "danger")
        return redirect(url_for('nueva_tarjeta'))
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    app.run(debug=True)
