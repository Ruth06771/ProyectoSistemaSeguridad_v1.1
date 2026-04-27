from flask import Flask, request, redirect, session, flash, url_for
from config.db import get_connection
import re

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro

# Ruta para actualizar persona
@app.route('/personas/editar', methods=['POST'])
def editar_persona():
    if 'usuario' not in session or session.get('rol') != 'admin':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    # Recibir datos
    id = int(request.form.get('id', 0))
    nombre_completo = request.form.get('nombre_completo', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
    correo = request.form.get('correo', '').strip()
    telefono_personal = request.form.get('telefono_personal', '').strip()
    documento_identidad = request.form.get('documento_identidad', '').strip()
    sexo = request.form.get('sexo', '').strip()
    tipo_sangre = request.form.get('tipo_sangre', '').strip()
    persona_emergencia = request.form.get('persona_emergencia', '').strip()
    telefono_emergencia = request.form.get('telefono_emergencia', '').strip()

    # Validaciones básicas
    if id <= 0 or not all([nombre_completo, fecha_nacimiento, correo, documento_identidad, sexo, persona_emergencia, telefono_emergencia]):
        flash("Todos los campos marcados como obligatorios son requeridos.", "danger")
        return redirect(url_for('editar_persona_form', id=id))

    # Validar correo
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        flash("Correo electrónico inválido.", "danger")
        return redirect(url_for('editar_persona_form', id=id))

    # Validar teléfonos numéricos
    if telefono_personal and not telefono_personal.isdigit():
        flash("El teléfono personal debe contener solo números.", "danger")
        return redirect(url_for('editar_persona_form', id=id))

    if not telefono_emergencia.isdigit():
        flash("El teléfono de emergencia debe contener solo números.", "danger")
        return redirect(url_for('editar_persona_form', id=id))

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Verificar duplicados
            cursor.execute(
                "SELECT id FROM personas WHERE (documento_identidad = %s OR correo = %s) AND id != %s",
                (documento_identidad, correo, id)
            )
            resultado = cursor.fetchone()
            if resultado:
                flash("Ya existe otra persona registrada con ese Documento de Identidad o Correo.", "danger")
                return redirect(url_for('editar_persona_form', id=id))

            # Actualizar persona
            cursor.execute(
                """UPDATE personas SET nombre_completo=%s, fecha_nacimiento=%s, correo=%s,
                   telefono_personal=%s, documento_identidad=%s, sexo=%s, tipo_sangre=%s,
                   persona_emergencia=%s, telefono_emergencia=%s
                   WHERE id=%s""",
                (nombre_completo, fecha_nacimiento, correo, telefono_personal, documento_identidad,
                 sexo, tipo_sangre, persona_emergencia, telefono_emergencia, id)
            )
            conn.commit()
            flash("Persona actualizada correctamente.", "success")
            return redirect(url_for('personas_index'))

    except Exception as e:
        flash(f"Error al actualizar la persona: {e}", "danger")
        return redirect(url_for('editar_persona_form', id=id))

    finally:
        try:
            conn.close()
        except:
            pass