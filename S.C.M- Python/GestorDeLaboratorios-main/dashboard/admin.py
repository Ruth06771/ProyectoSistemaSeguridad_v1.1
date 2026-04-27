from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # cambia por un secreto seguro

@app.route("/admin")
def admin_dashboard():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect(url_for("login", error="Acceso no autorizado"))
    return render_template("dashboard_admin.html", usuario=session["usuario"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

