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

def _normalize_permission_key(name):
    if not name:
        return ''
    key = name.strip().lower()
    key = re.sub(r'[áàäâã]', 'a', key)
    key = re.sub(r'[éèëê]', 'e', key)
    key = re.sub(r'[íìïî]', 'i', key)
    key = re.sub(r'[óòöôõ]', 'o', key)
    key = re.sub(r'[úùüû]', 'u', key)
    key = re.sub(r'[^a-z0-9]+', '_', key)
    return key.strip('_')


def get_role_id_by_name(conn, role_name):
    if not role_name:
        return None
    cur = conn.cursor()
    try:
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute("SELECT id FROM rol_sistema WHERE LOWER(nombre) = LOWER(?) AND estado = 1 LIMIT 1", (role_name,))
        else:
            cur.execute("SELECT id FROM rol_sistema WHERE LOWER(nombre) = LOWER(%s) AND estado = 1 LIMIT 1", (role_name,))
        row = cur.fetchone()
        if row:
            return row['id'] if hasattr(row, 'keys') else row[0]
        if conn.__class__.__module__.startswith('sqlite3'):
            cur.execute("SELECT id FROM rol_sistema WHERE LOWER(nombre) LIKE LOWER(?) AND estado = 1 LIMIT 1", (f"%{role_name}%",))
        else:
            cur.execute("SELECT id FROM rol_sistema WHERE LOWER(nombre) LIKE LOWER(%s) AND estado = 1 LIMIT 1", (f"%{role_name}%",))
        row = cur.fetchone()
        if row:
            return row['id'] if hasattr(row, 'keys') else row[0]
    finally:
        try:
            cur.close()
        except Exception:
            pass
    return None


def get_permissions_for_role(conn, role_id):
    permissions = {}
    modules = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, nombre FROM permisos")
        rows = cur.fetchall()
        assigned_map = {}
        if role_id:
            cur.execute("SELECT permiso_id, ver, crear, editar, eliminar FROM detalle_del_permiso WHERE rol_id = ? AND estado = 1", (role_id,))
            for row in cur.fetchall():
                permiso_id = row['permiso_id'] if hasattr(row, 'keys') else row[0]
                ver = row['ver'] if hasattr(row, 'keys') else row[1]
                crear = row['crear'] if hasattr(row, 'keys') else row[2]
                editar = row['editar'] if hasattr(row, 'keys') else row[3]
                eliminar = row['eliminar'] if hasattr(row, 'keys') else row[4]
                assigned_map[permiso_id] = {
                    'ver': bool(ver),
                    'crear': bool(crear),
                    'editar': bool(editar),
                    'eliminar': bool(eliminar)
                }

        for row in rows:
            permiso_id = row['id'] if hasattr(row, 'keys') else row[0]
            permiso_nombre = row['nombre'] if hasattr(row, 'keys') else row[1]
            key = _normalize_permission_key(permiso_nombre)
            permiso_flags = assigned_map.get(permiso_id, {
                'ver': False,
                'crear': False,
                'editar': False,
                'eliminar': False
            })
            assigned = permiso_flags['ver'] or permiso_flags['crear'] or permiso_flags['editar'] or permiso_flags['eliminar']
            permissions[key] = assigned
            permissions[f"{key}.ver"] = permiso_flags['ver']
            permissions[f"{key}.crear"] = permiso_flags['crear']
            permissions[f"{key}.editar"] = permiso_flags['editar']
            permissions[f"{key}.eliminar"] = permiso_flags['eliminar']
            modules.append({
                'id': permiso_id,
                'nombre': permiso_nombre,
                'key': key,
                'assigned': assigned,
                'ver': permiso_flags['ver'],
                'crear': permiso_flags['crear'],
                'editar': permiso_flags['editar'],
                'eliminar': permiso_flags['eliminar'],
            })
    finally:
        try:
            cur.close()
        except Exception:
            pass
    return permissions, modules


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

    # ONLY VALIDATE AGAINST DATABASE
    # First check DB usuario_sistema for credentials, then validate against personas table
    conn, err = try_get_connection()
    if conn and not err:
        try:
            cur = conn.cursor()
            try:
                # Step 1: Validate credentials in usuario_sistema
                if conn.__class__.__module__.startswith('sqlite3'):
                    cur.execute("SELECT id, persona_id FROM usuario_sistema WHERE nombre_usuario = ? AND contrasena = ? AND estado = 1", (correo, password))
                    row = cur.fetchone()
                else:
                    cur.execute("SELECT id, persona_id FROM usuario_sistema WHERE nombre_usuario = %s AND contrasena = %s AND estado = 1", (correo, password))
                    row = cur.fetchone()
                
                if row:
                    usuario_id = row['id'] if hasattr(row, 'keys') else row[0]
                    persona_id = (row['persona_id'] if hasattr(row, 'keys') else row[1]) if len(row) > 1 else None
                    
                    # Step 2: Look up the user in personas table to get real rol and nombre_completo
                    persona_data = None
                    if persona_id:
                        # If persona_id exists, use it to fetch persona data
                        if conn.__class__.__module__.startswith('sqlite3'):
                            cur.execute("SELECT id, nombre_completo, rol, estado FROM personas WHERE id = ? LIMIT 1", (persona_id,))
                        else:
                            cur.execute("SELECT id, nombre_completo, rol, estado FROM personas WHERE id = %s LIMIT 1", (persona_id,))
                        persona_data = cur.fetchone()
                    else:
                        # If persona_id is NULL, try to find by correo
                        if conn.__class__.__module__.startswith('sqlite3'):
                            cur.execute("SELECT id, nombre_completo, rol, estado FROM personas WHERE correo = ? LIMIT 1", (correo,))
                        else:
                            cur.execute("SELECT id, nombre_completo, rol, estado FROM personas WHERE correo = %s LIMIT 1", (correo,))
                        persona_data = cur.fetchone()
                    
                    # Step 3: Validate that persona exists and has valid status and rol
                    if not persona_data:
                        # Usuario exists in usuario_sistema but not in personas
                        print(f"[DEBUG] Usuario {correo} no encontrado en tabla personas")
                        return jsonify({"success": False, "error": "Usuario no registrado en el personal o sin permisos"}), 401
                    
                    persona_estado = persona_data['estado'] if hasattr(persona_data, 'keys') else persona_data[3]
                    if persona_estado != 1:
                        print(f"[DEBUG] Usuario {correo} inactivo en personas (estado != 1)")
                        return jsonify({"success": False, "error": "Usuario inactivo"}), 401
                    
                    rol_persona = persona_data['rol'] if hasattr(persona_data, 'keys') else persona_data[2]
                    nombre_completo = persona_data['nombre_completo'] if hasattr(persona_data, 'keys') else persona_data[1]
                    
                    # Step 4: Deny access if rol is 'Invitado'
                    if rol_persona and rol_persona.lower() == 'invitado':
                        print(f"[DEBUG] Usuario {correo} tiene rol 'Invitado', acceso denegado")
                        return jsonify({"success": False, "error": "Usuario no registrado en el personal o sin permisos"}), 401
                    
                    # Step 5: Assign dynamic rol from personas table
                    session['usuario'] = correo
                    session['nombre'] = nombre_completo
                    session['rol'] = rol_persona if rol_persona else 'invitado'
                    # If the user has a corresponding rol_sistema entry, load permissions for that role.
                    role_id = get_role_id_by_name(conn, session['rol'])
                    permissions, permissions_modules = get_permissions_for_role(conn, role_id)
                    session['permissions'] = permissions
                    session['permission_modules'] = permissions_modules
                    
                    try:
                        log_action(conn, 'auth', entidad_id=usuario_id, entidad_tipo='usuario', accion='login', usuario=correo, descripcion=f'Login exitoso usuario={correo} rol={session["rol"]}')
                    except Exception:
                        pass
                    
                    return jsonify({
                        "success": True,
                        "rol": session['rol'],
                        "usuario": correo,
                        "nombre": nombre_completo,
                        "permissions": permissions,
                        "permission_modules": permissions_modules
                    })
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

    # EMERGENCY FALLBACK ONLY: If database is completely unavailable,
    # allow ONLY the emergency IT backup account with hardcoded credentials
    print(f"[DEBUG] BD no disponible. Verificando credencial de emergencia para {correo}...")
    if (correo == EMERGENCY_BACKUP_USER['correo'] and 
        password == EMERGENCY_BACKUP_USER['password']):
        session['usuario'] = EMERGENCY_BACKUP_USER['correo']
        session['rol'] = EMERGENCY_BACKUP_USER['rol']
        session['nombre'] = EMERGENCY_BACKUP_USER['nombre']
        session['permissions'] = {
            'configuracion': True,
            'configuracion.ver': True,
            'configuracion.crear': True,
            'configuracion.editar': True,
            'configuracion.eliminar': True,
            'enrolar': True,
            'enrolar.ver': True,
            'enrolar.crear': True,
            'enrolar.editar': True,
            'enrolar.eliminar': True,
            'seguridad': True,
            'seguridad.ver': True,
            'seguridad.crear': True,
            'seguridad.editar': True,
            'seguridad.eliminar': True,
            'reportes': True,
            'reportes.ver': True,
            'reportes.crear': True,
            'reportes.editar': True,
            'reportes.eliminar': True
        }
        session['permission_modules'] = [
            {'id': 1, 'nombre': 'Configuración', 'key': 'configuracion', 'assigned': True, 'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            {'id': 2, 'nombre': 'Enrolar', 'key': 'enrolar', 'assigned': True, 'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            {'id': 3, 'nombre': 'Seguridad', 'key': 'seguridad', 'assigned': True, 'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            {'id': 4, 'nombre': 'Reportes', 'key': 'reportes', 'assigned': True, 'ver': True, 'crear': True, 'editar': True, 'eliminar': True}
        ]
        print(f"[WARN] ⚠️ ACCESO DE EMERGENCIA USADO: {correo} (BD no disponible)")
        return jsonify({
            "success": True, 
            "rol": session['rol'], 
            "usuario": correo, 
            "nombre": EMERGENCY_BACKUP_USER['nombre'],
            "permissions": session['permissions'],
            "permission_modules": session['permission_modules'],
            "emergency": True
        })
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
        return jsonify({
            "usuario": session.get('usuario'),
            "rol": session.get('rol'),
            "nombre": session.get('nombre'),
            "permissions": session.get('permissions', {}),
            "permission_modules": session.get('permission_modules', [])
        })
    return jsonify({"usuario": None}), 401


@app.route('/api/admins/create', methods=['POST'])
def api_create_admin():
    """Create a privileged admin user (max 5). Protected by ADMIN_SETUP_TOKEN env var."""
    data = request.get_json() or {}
    # For simplicity creation does not require a setup token anymore.
    # The endpoint accepts only email and password in the request body.
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
        # enforce max admins
        current = count_admins(conn)
        if current >= MAX_ADMIN_COUNT:
            return jsonify({'success': False, 'error': 'limit_reached', 'message': f'Maximo {MAX_ADMIN_COUNT} admins permitidos'}), 400

        cur = conn.cursor()
        try:
            # Require that the email already exists in personas and is active
            placeholder = '?'
            params = (email,)
            if not conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '%s'
            if conn.__class__.__module__.startswith('sqlite3'):
                cur.execute(f"SELECT id, rol, estado FROM personas WHERE LOWER(correo) = LOWER(?) LIMIT 1", (email,))
            else:
                cur.execute(f"SELECT id, rol, estado FROM personas WHERE LOWER(correo) = LOWER(%s) LIMIT 1", (email,))
            persona = cur.fetchone()
            if not persona:
                return jsonify({'success': False, 'error': 'persona_not_found', 'message': 'El correo debe estar registrado previamente en el sistema de personas.'}), 400
            persona_id = persona['id'] if hasattr(persona, 'keys') else persona[0]
            persona_estado = persona['estado'] if hasattr(persona, 'keys') else persona[2]
            if persona_estado != 1:
                return jsonify({'success': False, 'error': 'persona_inactive', 'message': 'La persona asociada al correo no está activa.'}), 400

            # Determine role id from persona. If persona.rol not mapped, set rol_id NULL.
            persona_rol = persona['rol'] if hasattr(persona, 'keys') else persona[1]
            rol_id = get_role_id_by_name(conn, persona_rol) if persona_rol else None

            # Ensure usuario_sistema doesn't already exist
            if conn.__class__.__module__.startswith('sqlite3'):
                cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = ? LIMIT 1", (email,))
            else:
                cur.execute("SELECT id FROM usuario_sistema WHERE nombre_usuario = %s LIMIT 1", (email,))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'exists', 'message': 'Usuario ya existe'}), 400

            # Insert usuario_sistema linking to persona and using persona's role id
            if conn.__class__.__module__.startswith('sqlite3'):
                if rol_id:
                    cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (?, ?, ?, ?, 1)", (persona_id, email, password, rol_id))
                else:
                    cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (?, ?, ?, NULL, 1)", (persona_id, email, password))
            else:
                if rol_id:
                    cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (%s, %s, %s, %s, 1)", (persona_id, email, password, rol_id))
                else:
                    cur.execute("INSERT INTO usuario_sistema (persona_id, nombre_usuario, contrasena, rol_id, estado) VALUES (%s, %s, %s, NULL, 1)", (persona_id, email, password))
            try:
                conn.commit()
            except Exception:
                pass

            try:
                log_action(conn, 'usuarios', entidad_id=None, entidad_tipo='usuario', accion='create', usuario=session.get('usuario') if session else None, descripcion=f'Usuario creado vinculado a persona {persona_id} correo={email}')
            except Exception:
                pass
            return jsonify({'success': True})
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

@app.route('/api/admins', methods=['GET'])
def api_list_admins():
    conn, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cur = conn.cursor()
        try:
            if conn.__class__.__module__.startswith('sqlite3'):
                cur.execute('SELECT id, nombre_usuario, contrasena FROM usuario_sistema WHERE estado = 1')
            else:
                cur.execute('SELECT id, nombre_usuario, contrasena FROM usuario_sistema WHERE estado = %s', (1,))
            rows = cur.fetchall()
            if rows and hasattr(rows[0], 'keys'):
                admins = [dict(r) for r in rows]
            else:
                admins = rows
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify(admins)
    except Exception:
        return jsonify({'error': 'query_failed'}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route('/api/admins/<int:id>', methods=['DELETE'])
def api_delete_admin(id):
    conn, err = try_get_connection()
    if err:
        return jsonify({'error': 'db_connection', 'message': err}), 500
    try:
        cur = conn.cursor()
        try:
            placeholder = '%s'
            params = (id,)
            if conn.__class__.__module__.startswith('sqlite3'):
                placeholder = '?'
            cur.execute(f'DELETE FROM usuario_sistema WHERE id = {placeholder}', params)
            conn.commit()
            try:
                log_action(conn, 'usuarios', entidad_id=id, entidad_tipo='usuario', accion='delete', usuario=session.get('usuario') if session else None, descripcion=f'Admin eliminado id={id}')
            except Exception:
                pass
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return jsonify({'success': True})
    except Exception:
        return jsonify({'error': 'delete_failed'}), 500
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
