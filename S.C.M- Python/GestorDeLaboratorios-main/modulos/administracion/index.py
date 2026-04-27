from flask import Flask, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'TU_SECRETO_AQUI'  # Cambiar por algo seguro

# Ruta del módulo de administración
@app.route('/admin/modulo')
def admin_modulo():
    # Verificamos que el usuario esté autenticado y sea admin
    if 'usuario' not in session or session.get('rol') != 'admin':
        return redirect(url_for('login', error="Acceso no autorizado"))

   
    return render_template_string(html)

# Ruta de login (ejemplo)
@app.route('/login')
def login():
    error = request.args.get('error')
    return f"Login Page - Error: {error}"

if __name__ == '__main__':
    app.run(debug=True)
