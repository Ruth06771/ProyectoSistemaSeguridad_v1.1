from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os

# Add project root to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.db import get_connection

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro

# ============================================================
# CUENTA DE RESPALDO DE EMERGENCIA PARA TI (NO ELIMINAR)
# Úsese SOLO en caso de que la BD sea inaccesible
# ============================================================
EMERGENCY_BACKUP_USER = {
    "correo": "lab.tecnologia@ueb.edu.bo",
    "password": "FacultadTecnologia2026",
    "rol": "administrador",
    "nombre": "Administrador Facultad Tecnología"
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
    correo = request.form.get('correo', '').strip().lower()
    password = request.form.get('password', '')
    
    # Try to authenticate from database
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Validate against usuario_sistema
            cur.execute("SELECT id, nombre_usuario FROM usuario_sistema WHERE nombre_usuario = ? AND contrasena = ? AND estado = 1", (correo, password))
            row = cur.fetchone()
            
            if row:
                session['usuario'] = correo
                session['rol'] = 'administrador'  # Or fetch from personas table
                return redirect(url_for('dashboard', rol=session['rol']))
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        # Only allow emergency backup account if database is down
        if correo == EMERGENCY_BACKUP_USER['correo'] and password == EMERGENCY_BACKUP_USER['password']:
            session['usuario'] = correo
            session['rol'] = EMERGENCY_BACKUP_USER['rol']
            print(f"[WARN] Emergency backup account used (database unavailable)")
            return redirect(url_for('dashboard', rol=session['rol']))
        else:
            return redirect(url_for('login', error="Correo o contraseña incorrectos (BD no disponible)"))
    
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
