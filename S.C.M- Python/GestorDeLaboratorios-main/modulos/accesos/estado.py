from flask import Blueprint, request, redirect, session, url_for, flash
from config.db import get_connection

# Crear blueprint para accesos
accesos_bp = Blueprint("accesos", __name__, url_prefix="/accesos")


@accesos_bp.route("/estado", methods=["POST"])
def cambiar_estado():
    # 1. Verificar sesión y rol
    if "usuario" not in session or session.get("rol") != "admin":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("auth.login"))

    # 2. Validar parámetros
    try:
        tarjeta_id = int(request.form.get("id", 0))
    except ValueError:
        tarjeta_id = 0

    nuevo_estado = request.form.get("estado", "")
    if tarjeta_id <= 0 or nuevo_estado not in ["habilitada", "inhabilitada"]:
        flash("Parámetros inválidos.", "danger")
        return redirect(url_for("accesos.index"))

    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()

        # adapt placeholders
        placeholder = '%s'
        if conexion.__class__.__module__.startswith('sqlite3'):
            placeholder = '?'

        # 3. Obtener datos de la tarjeta
        cursor.execute(f"SELECT uid, nombre_completo FROM tarjetas WHERE id = {placeholder}", (tarjeta_id,))
        tarjeta = cursor.fetchone()

        if not tarjeta:
            flash("Tarjeta no encontrada.", "danger")
            return redirect(url_for("accesos.index"))

        # normalize row
        if hasattr(tarjeta, 'keys'):
            uid = tarjeta.get('uid')
            nombre_completo = tarjeta.get('nombre_completo')
        else:
            # sqlite may return tuple
            uid = tarjeta[0]
            nombre_completo = tarjeta[1] if len(tarjeta) > 1 else ''

        # 4. Actualizar estado
        cursor.execute(f"UPDATE tarjetas SET estado = {placeholder} WHERE id = {placeholder}", (nuevo_estado, tarjeta_id))

        # 5. Registrar historial
        accion = "alta" if nuevo_estado == "habilitada" else "baja"
        usuario = session.get("usuario")

        sql_hist = """
            INSERT INTO historial_tarjetas 
            (tarjeta_id, uid, nombre_completo, accion, ejecutado_por)
            VALUES (%s, %s, %s, %s, %s)
        """
        if conexion.__class__.__module__.startswith('sqlite3'):
            sql_hist = sql_hist.replace('%s', '?')
        cursor.execute(sql_hist, (tarjeta_id, uid, nombre_completo, accion, usuario))

        conexion.commit()
        # 6. Mensaje de éxito
        flash("Tarjeta actualizada correctamente y acción registrada.", "success")
    except Exception as e:
        try:
            conexion.rollback()
        except Exception:
            pass
        flash(f"Error al actualizar tarjeta: {str(e)}", "danger")
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass

    return redirect(url_for("accesos.index"))