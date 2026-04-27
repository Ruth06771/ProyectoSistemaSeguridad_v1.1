from flask import Flask, request, redirect, url_for, session, flash
from config.db import get_connection
import pymysql
import re

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"  # Cambiar por algo seguro

# Ruta para registrar persona
@app.route("/personas/registrar", methods=["POST"])
def registrar_persona():
    # Verificar sesión y rol
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect(url_for("login", error="Acceso no autorizado"))

    # Obtener y limpiar datos
    nombre_completo = request.form.get("nombre_completo", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
    correo = request.form.get("correo", "").strip()
    telefono_personal = request.form.get("telefono_personal", "").strip()
    documento_identidad = request.form.get("documento_identidad", "").strip()
    sexo = request.form.get("sexo", "").strip()
    tipo_sangre = request.form.get("tipo_sangre", "").strip()
    persona_emergencia = request.form.get("persona_emergencia", "").strip()
    telefono_emergencia = request.form.get("telefono_emergencia", "").strip()

    # Validaciones
    if not all([nombre_completo, fecha_nacimiento, correo, documento_identidad, sexo, persona_emergencia, telefono_emergencia]):
        flash("Todos los campos obligatorios deben estar completos.", "error")
        return redirect(url_for("registrar_form"))

    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        flash("Correo electrónico inválido.", "error")
        return redirect(url_for("registrar_form"))

    if telefono_personal and not telefono_personal.isdigit():
        flash("El teléfono personal debe contener solo números.", "error")
        return redirect(url_for("registrar_form"))

    if not telefono_emergencia.isdigit():
        flash("El teléfono de emergencia debe contener solo números.", "error")
        return redirect(url_for("registrar_form"))

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Verificar duplicados
            sql_check = "SELECT id FROM personas WHERE documento_identidad=%s OR correo=%s"
            cursor.execute(sql_check, (documento_identidad, correo))
            if cursor.fetchone():
                flash("Ya existe una persona registrada con ese Documento de Identidad o Correo.", "error")
                return redirect(url_for("registrar_form"))

            # Insertar en la base de datos
            sql_insert = """
                INSERT INTO personas (
                    nombre_completo, fecha_nacimiento, correo, telefono_personal,
                    documento_identidad, sexo, tipo_sangre, persona_emergencia, telefono_emergencia
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (
                nombre_completo,
                fecha_nacimiento,
                correo,
                telefono_personal,
                documento_identidad,
                sexo,
                tipo_sangre,
                persona_emergencia,
                telefono_emergencia
            ))
            conn.commit()
            flash("✅ Persona registrada correctamente.", "success")
            return redirect(url_for("index"))
    except pymysql.MySQLError as e:
        flash(f"❌ Error al guardar la persona: {str(e)}", "error")
        return redirect(url_for("registrar_form"))
    finally:
        try:
            conn.close()
        except:
            pass

