from flask import Flask, request, session, jsonify
from flask_cors import CORS
import os
import sys
from flask import send_from_directory, render_template
import re

# Asegurar que el directorio raíz del proyecto esté en sys.path para permitir
# imports como `from modulos...` cuando se ejecuta este archivo directamente.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# After ensuring project root is on sys.path, import DB helpers
from config.db import get_connection, EMAIL_ALLOWED_DOMAINS, log_action

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI" 
CORS(app, supports_credentials=True)

# If a built frontend exists, serve it from the `frontend/dist` directory at the root.
FRONTEND_DIST = os.path.abspath(os.path.join(ROOT, 'frontend', 'dist'))
if os.path.isdir(FRONTEND_DIST):
    @app.route('/')
    def serve_frontend_index():
        return send_from_directory(FRONTEND_DIST, 'index.html')

    @app.route('/assets/<path:filename>')
    def serve_frontend_assets(filename):
        return send_from_directory(os.path.join(FRONTEND_DIST, 'assets'), filename)

# Registrar blueprints de APIs modulares
try:
    from modulos.administracion.personas.personas_api import personas_api
    app.register_blueprint(personas_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

try:
    from modulos.accesos.tarjetas_api import tarjetas_api
    app.register_blueprint(tarjetas_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

try:
    from modulos.accesos.enrolar_api import enrolar_api
    app.register_blueprint(enrolar_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    # don't raise here to avoid breaking startup if module missing

try:
    from modulos.reportes.reportes_api import reportes_api
    app.register_blueprint(reportes_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

# Register PDF export blueprints (optional; may require reportlab)
try:
    from modulos.reportes.exportar_pdf_tarjetas import bp as exportar_pdf_tarjetas_bp
    app.register_blueprint(exportar_pdf_tarjetas_bp)
except Exception:
    import traceback
    traceback.print_exc()

# Optional personal access PDF report (reportlab)
try:
    from modulos.reportes.exportar_pdf_personal import bp as exportar_pdf_personal_bp
    app.register_blueprint(exportar_pdf_personal_bp)
except Exception:
    import traceback
    traceback.print_exc()

# Optional Excel export endpoints for reportes
try:
    from modulos.reportes.exportar_excel import bp as exportar_excel_bp
    app.register_blueprint(exportar_excel_bp)
except Exception:
    import traceback
    traceback.print_exc()

# Optional tarjeta historial PDF report (weasyprint)
try:
    from modulos.reportes.exportar_pdf_tarjeta_historial_accesos import bp as exportar_pdf_tarjeta_historial_bp
    app.register_blueprint(exportar_pdf_tarjeta_historial_bp)
except Exception:
    import traceback
    traceback.print_exc()

try:
    from modulos.administracion.usuarios.usuarios_api import usuarios_api
    app.register_blueprint(usuarios_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

try:
    from modulos.administracion.bitacora_api import bitacora_api
    app.register_blueprint(bitacora_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

try:
    from modulos.administracion.roles_permisos_api import roles_api
    app.register_blueprint(roles_api)
except Exception as e:
    import traceback
    traceback.print_exc()
    # non-fatal

try:
    from modulos.administracion.dispositivos_api import dispositivos_api
    app.register_blueprint(dispositivos_api)
except Exception:
    import traceback
    traceback.print_exc()

try:
    from modulos.registro.tipo_movimiento_api import tipo_movimiento_api
    app.register_blueprint(tipo_movimiento_api)
except Exception:
    import traceback
    traceback.print_exc()

try:
    from modulos.registro.tipo_dispositivo_api import tipo_dispositivo_api
    app.register_blueprint(tipo_dispositivo_api)
except Exception:
    import traceback
    traceback.print_exc()

try:
    from modulos.registro.tipo_registro_api import tipo_registro_api
    app.register_blueprint(tipo_registro_api)
except Exception:
    import traceback
    traceback.print_exc()

# Register ESP device API
try:
    from auth.esp_api import esp_api
    app.register_blueprint(esp_api)
except Exception:
    import traceback
    traceback.print_exc()

usuarios = {
    "admin@uni.edu": {"password": "1234", "rol": "administrador"},
    "user@uni.edu": {"password": "abcd", "rol": "estudiante"}
}

# Admin seeding & limits
ADMIN_EMAILS_ENV = os.environ.get('ADMIN_EMAILS', '').strip()
ADMIN_SETUP_TOKEN = os.environ.get('ADMIN_SETUP_TOKEN', '').strip()
MAX_ADMIN_COUNT = 5


def try_get_connection():
    try:
        conn = get_connection()
        return conn, None
    except Exception as e:
        return None, str(e)


def count_admins(connection):
    try:
        cur = connection.cursor()
        try:
            cur.execute("SELECT COUNT(*) as c FROM usuario_sistema WHERE estado=1")
            row = cur.fetchone()
            if row:
                # sqlite3.Row or tuple
                return row['c'] if hasattr(row, 'keys') else row[0]
        finally:
            try:
                cur.close()
            except Exception:
                pass
    except Exception:
        pass
    return 0


def create_admin_if_not_exists(connection, email, password):
    # assumes connection passed
    try:
        cur = connection.cursor()
        try:
            # check exists
            if connection.__class__.__module__.startswith('sqlite3'):
                cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = ? LIMIT 1", (email,))
            else:
                cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = %s LIMIT 1", (email,))
            row = cur.fetchone()
            if row:
                return False
            # insert
            if connection.__class__.__module__.startswith('sqlite3'):
                cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (NULL, ?, ?, NULL, 1)", (email, password))
            else:
                cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (NULL, %s, %s, NULL, 1)", (email, password))
            try:
                connection.commit()
            except Exception:
                pass
            return True
        finally:
            try:
                cur.close()
            except Exception:
                pass
    except Exception:
        return False


# Seed admins from environment at startup (limit to MAX_ADMIN_COUNT)
if ADMIN_EMAILS_ENV:
    emails = [e.strip().lower() for e in ADMIN_EMAILS_ENV.split(',') if e.strip()]
    if emails:
        conn, err = try_get_connection()
        if conn and not err:
            try:
                existing = count_admins(conn)
                for e in emails:
                    if existing >= MAX_ADMIN_COUNT:
                        break
                    # validate domain
                    domain = e.split('@')[-1].lower() if '@' in e else ''
                    if EMAIL_ALLOWED_DOMAINS and domain not in EMAIL_ALLOWED_DOMAINS:
                        continue
                    # create with a random temporary password (admin should change later)
                    # for simplicity use 'changeme' as default password; instruct admin to change it
                    created = create_admin_if_not_exists(conn, e, 'changeme')
                    if created:
                        existing += 1
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

@app.route('/api/login', methods=['POST'])
def api_login():
    # Debug: log incoming request info to help diagnose proxy/connection issues
    try:
        data = request.get_json()
    except Exception:
        data = None
    print(f"[DEBUG] /api/login called from {request.remote_addr} method={request.method} content_type={request.content_type}")
    print(f"[DEBUG] payload: {data}")
    correo = (data.get('correo') or '').strip().lower()
    password = data.get('password')

    # First check DB usuario_sistema for credentials
    conn, err = try_get_connection()
    if conn and not err:
        try:
            cur = conn.cursor()
            try:
                if conn.__class__.__module__.startswith('sqlite3'):
                    cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = ? AND contrasena = ? AND estado = 1", (correo, password))
                    row = cur.fetchone()
                else:
                    cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = %s AND contrasena = %s AND estado = 1", (correo, password))
                    row = cur.fetchone()
                if row:
                    session['usuario'] = correo
                    session['rol'] = 'admin'
                    try:
                        log_action(conn, 'auth', entidad_id=row['id'] if hasattr(row, 'keys') and 'id' in row else None, entidad_tipo='usuario', accion='login', usuario=correo, descripcion=f'Login exitoso usuario={correo}')
                    except Exception:
                        pass
                    return jsonify({"success": True, "rol": session['rol'], "usuario": correo})
            finally:
                try:
                    cur.close()
                except Exception:
                    pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # fallback to simple in-memory usuarios dict (legacy)
    if correo in usuarios and usuarios[correo]['password'] == password:
        session['usuario'] = correo
        session['rol'] = usuarios[correo]['rol']
        # Log in-memory fallback login
        try:
            conn, err = try_get_connection()
            if conn and not err:
                try:
                    log_action(conn, 'auth', entidad_id=None, entidad_tipo='usuario', accion='login', usuario=correo, descripcion=f'Login exitoso (fallback) usuario={correo}')
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
        except Exception:
            pass
        return jsonify({"success": True, "rol": session['rol'], "usuario": correo})
    else:
        return jsonify({"success": False, "error": "Correo o contraseña incorrectos"}), 401


@app.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint for debugging from Vite/proxy."""
    return jsonify({"pong": True})


# Serve the university logo from the project's static/img directory explicitly.
@app.route('/img/ueb-logo.png')
def serve_logo():
    # Serve an available UEB logo file. Support alternative filenames (e.g. uebLogo.png.jpg).
    logo_dir = os.path.join(ROOT, 'static', 'img')
    # Prefer canonical name, otherwise try alternatives by pattern
    candidates = ['ueb-logo.png', 'uebLogo.png', 'ueb-logo.jpg', 'uebLogo.png.jpg', 'ueb-logo.jpeg']
    for name in candidates:
        path = os.path.join(logo_dir, name)
        if os.path.exists(path):
            return send_from_directory(logo_dir, name)
    # Fallback: pick any file that starts with 'ueb' (case-insensitive)
    try:
        for f in os.listdir(logo_dir):
            if f.lower().startswith('ueb') and os.path.isfile(os.path.join(logo_dir, f)):
                return send_from_directory(logo_dir, f)
    except Exception:
        pass
    # If nothing found, return 404
    return ('Logo not found', 404)


# Alias para que el frontend que busca /ueb-logo.png también funcione
@app.route('/ueb-logo.png')
def serve_logo_root():
    # Alias route: reuse same detection logic as above
    logo_dir = os.path.join(ROOT, 'static', 'img')
    candidates = ['ueb-logo.png', 'uebLogo.png', 'ueb-logo.jpg', 'uebLogo.png.jpg', 'ueb-logo.jpeg']
    for name in candidates:
        path = os.path.join(logo_dir, name)
        if os.path.exists(path):
            return send_from_directory(logo_dir, name)
    try:
        for f in os.listdir(logo_dir):
            if f.lower().startswith('ueb') and os.path.isfile(os.path.join(logo_dir, f)):
                return send_from_directory(logo_dir, f)
    except Exception:
        pass
    return ('Logo not found', 404)

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    # Attempt to log logout action (best-effort)
    try:
        conn, err = try_get_connection()
        if conn and not err:
            try:
                log_action(conn, 'auth', entidad_id=None, entidad_tipo='usuario', accion='logout', usuario=None, descripcion='Logout')
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
    except Exception:
        pass

    return jsonify({"success": True})

@app.route('/api/session', methods=['GET'])
def api_session():
    if 'usuario' in session:
        return jsonify({"usuario": session['usuario'], "rol": session['rol']})
    return jsonify({"usuario": None}), 401


@app.route('/api/admins/create', methods=['POST'])
def api_create_admin():
    """Create a privileged admin user (max 5). Protected by ADMIN_SETUP_TOKEN env var."""
    data = request.get_json() or {}
    token = data.get('token') or ''
    if not ADMIN_SETUP_TOKEN or token != ADMIN_SETUP_TOKEN:
        return jsonify({'success': False, 'error': 'not_authorized'}), 403
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or 'changeme'
    # validate email format and domain
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if not email_re.match(email):
        return jsonify({'success': False, 'error': 'invalid_email'}), 400
    if EMAIL_ALLOWED_DOMAINS:
        domain = email.split('@')[-1].lower()
        if domain not in EMAIL_ALLOWED_DOMAINS:
            return jsonify({'success': False, 'error': 'email_domain_not_allowed'}), 400

    conn, err = try_get_connection()
    if err:
        return jsonify({'success': False, 'error': 'db_connection', 'message': err}), 500
    try:
        current = count_admins(conn)
        if current >= MAX_ADMIN_COUNT:
            return jsonify({'success': False, 'error': 'limit_reached', 'message': f'Maximo {MAX_ADMIN_COUNT} admins permitidos'}), 400
        created = create_admin_if_not_exists(conn, email, password)
        if created:
                try:
                    log_action(conn, 'usuarios', entidad_id=None, entidad_tipo='usuario', accion='create', usuario=session.get('usuario') if session else None, descripcion=f'Admin creado {email}')
                except Exception:
                    pass
                return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'exists_or_error'}), 400
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ...existing code...

if __name__ == '__main__':
    # For debugging locally prefer a single stable process (no reloader)
    # to avoid issues with process forking on Windows that can make the
    # dev server intermittently not accept connections from other processes
    # (like Vite's proxy). Use debug=False here while diagnosing.
    print('[INFO] Starting Flask without reloader (debug=False) on 0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
