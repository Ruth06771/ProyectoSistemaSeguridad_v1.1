from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro

# Datos de ejemplo (simulando una base de datos)
usuarios = {
    "admin@uni.edu": {"password": "1234", "rol": "administrador"}, 
    "user@uni.edu": {"password": "abcd", "rol": "estudiante"}
}

@app.route('/')
def login():
    # Si ya está logueado, redirigir al dashboard
    if 'usuario' in session:
        rol = session['rol']
        return redirect(url_for('dashboard', rol=rol))
    
    error = request.args.get('error')  # Captura el error si existe
    return render_template('login.html', error=error)

@app.route('/validar_login', methods=['POST'])
def validar_login():
    correo = request.form['correo']
    password = request.form['password']
    
    if correo in usuarios and usuarios[correo]['password'] == password:
        session['usuario'] = correo
        session['rol'] = usuarios[correo]['rol']
        return redirect(url_for('dashboard', rol=session['rol']))
    else:
        return redirect(url_for('login', error="Correo o contraseña incorrectos"))

@app.route('/dashboard/<rol>')
def dashboard(rol):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return f"Bienvenido al dashboard de {rol}. Usuario: {session['usuario']}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
