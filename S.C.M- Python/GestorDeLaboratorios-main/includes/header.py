from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # cámbialo por algo seguro

@app.route("/admin")
def admin_dashboard():
    # Verificar que el usuario esté autenticado
    if "usuario" not in session:
        return redirect(url_for("login", error="Acceso no autorizado"))
    
    return render_template("dashboard/admin.html", usuario=session["usuario"])

@app.route("/login")
def login():
    # Aquí deberías mostrar el formulario de login
    return "Página de login (login.html)"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
