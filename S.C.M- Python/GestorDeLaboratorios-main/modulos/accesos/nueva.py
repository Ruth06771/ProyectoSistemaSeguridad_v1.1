from flask import Flask, request, redirect, flash, get_flashed_messages
from flask import render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'TU_SECRETO_AQUI'  # Cambiar por algo seguro

# Crear base de datos y tabla si no existe
def init_db():
    conn = sqlite3.connect('tarjetas.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarjetas (
            uid TEXT PRIMARY KEY,
            nombre_completo TEXT NOT NULL,
            correo TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()




@app.route("/", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        uid = request.form.get("uid", "").strip()
        nombre_completo = request.form.get("nombre_completo", "").strip()
        correo = request.form.get("correo", "").strip()

        if not uid or not nombre_completo or not correo:
            flash("Todos los campos son obligatorios.", "danger")
        else:
            try:
                conn = sqlite3.connect('tarjetas.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tarjetas (uid, nombre_completo, correo) VALUES (?, ?, ?)",
                               (uid, nombre_completo, correo))
                conn.commit()
                conn.close()
                flash("Tarjeta registrada correctamente.", "success")
            except sqlite3.IntegrityError:
                flash("La UID ya está registrada.", "danger")

        return redirect("/")

    # Mostrar tarjetas registradas
    conn = sqlite3.connect('tarjetas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uid, nombre_completo, correo FROM tarjetas")
    tarjetas = cursor.fetchall()
    conn.close()

    return render_template_string(HTML_TEMPLATE, tarjetas=tarjetas)

if __name__ == "__main__":
    app.run(debug=True)
