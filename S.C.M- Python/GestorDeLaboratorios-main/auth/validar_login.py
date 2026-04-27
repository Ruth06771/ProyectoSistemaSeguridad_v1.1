from flask import Flask, request, redirect, session, url_for, render_template
import pymysql
from config.db import get_connection

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()

        if not correo or not password:
            return redirect(url_for("login", error="Debes completar todos los campos."))

        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, password, rol, estado FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            if usuario["estado"] != "activo":
                return redirect(url_for("login", error="El usuario está inactivo."))
            if usuario["password"] == password:
                session["usuario"] = usuario["nombre"]
                session["rol"] = usuario["rol"]
                session["id"] = usuario["id"]
                return redirect(url_for("dashboard", rol=usuario["rol"]))
            else:
                return redirect(url_for("login", error="Contraseña incorrecta."))
        else:
            return redirect(url_for("login", error="Correo no registrado."))
    else:
        error = request.args.get("error")
        return render_template("auth/login.html", error=error)

@app.route("/dashboard/<rol>")
def dashboard(rol):
    if "usuario" not in session:
        return redirect(url_for("login", error="Acceso no autorizado"))
    return render_template(f"dashboard/{rol}.html", usuario=session["usuario"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
