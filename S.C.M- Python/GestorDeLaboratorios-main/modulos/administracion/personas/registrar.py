from flask import Flask, render_template, request, redirect, url_for, session, flash
from config.db import get_connection

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"
@app.route("/personas/nuevo", methods=["GET", "POST"])
def registrar_persona():
    if request.method == "POST":
        datos = {
            "nombre_completo": request.form.get("nombre_completo", "").strip(),
            "fecha_nacimiento": request.form.get("fecha_nacimiento", ""),
            "correo": request.form.get("correo", "").strip(),
            "telefono_personal": request.form.get("telefono_personal", "").strip(),
            "documento_identidad": request.form.get("documento_identidad", "").strip(),
            "sexo": request.form.get("sexo", ""),
            "tipo_sangre": request.form.get("tipo_sangre", ""),
            "persona_emergencia": request.form.get("persona_emergencia", "").strip(),
            "telefono_emergencia": request.form.get("telefono_emergencia", "").strip(),
        }

        # Validar campos obligatorios
        if not all([datos["nombre_completo"], datos["fecha_nacimiento"], datos["correo"],
                    datos["documento_identidad"], datos["sexo"],
                    datos["persona_emergencia"], datos["telefono_emergencia"]]):
            flash("Debes completar todos los campos obligatorios.", "danger")
            return redirect(url_for("registrar_persona"))

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO personas 
                (nombre_completo, fecha_nacimiento, correo, telefono_personal, 
                documento_identidad, sexo, tipo_sangre, persona_emergencia, telefono_emergencia)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                datos["nombre_completo"], datos["fecha_nacimiento"], datos["correo"],
                datos["telefono_personal"], datos["documento_identidad"], datos["sexo"],
                datos["tipo_sangre"], datos["persona_emergencia"], datos["telefono_emergencia"]
            ))
            connection.commit()
            try:
                new_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                if new_id:
                    placeholder = '%s'
                    if connection.__class__.__module__.startswith('sqlite3'):
                        placeholder = '?'
                    cursor.execute(
                        f"INSERT INTO historial_acciones (modulo, entidad_id, entidad_tipo, accion, usuario, descripcion) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})",
                        ('personas', new_id, 'persona', 'create', session.get('usuario') if session else None, f'Persona registrada {datos["nombre_completo"]}')
                    )
                    connection.commit()
            except Exception:
                pass
            connection.close()
            flash("Persona registrada con éxito.", "success")
            return redirect(url_for("registrar_persona"))
        except Exception as e:
            flash(f"Error al registrar persona: {str(e)}", "danger")
            return redirect(url_for("registrar_persona"))

    return render_template("personas/registrar.html")

if __name__ == "__main__":
    app.run(debug=True)
