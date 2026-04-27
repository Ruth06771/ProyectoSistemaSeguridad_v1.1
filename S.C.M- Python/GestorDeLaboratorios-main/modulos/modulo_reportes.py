from flask import Flask, render_template
from config.db import get_connection

app = Flask(__name__)

@app.route('/historial_accesos')
def historial_accesos():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            sql = "SELECT * FROM historial_accesos ORDER BY fecha DESC"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            if resultados and hasattr(resultados[0], 'keys'):
                resultados = [dict(r) for r in resultados]
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

    return render_template('historial_accesos.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)
