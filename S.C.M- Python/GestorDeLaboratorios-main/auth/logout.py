from flask import Flask, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Necesario para usar sesiones

@app.route("/logout")
def logout():
    # Destruir la sesión (equivalente a session_destroy())
    session.clear()
    # Redirigir al login
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return "Aquí iría tu página de login (login.html)"
