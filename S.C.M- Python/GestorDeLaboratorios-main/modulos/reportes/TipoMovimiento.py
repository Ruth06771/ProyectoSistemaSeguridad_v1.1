from flask import Flask, jsonify
from flask_cors import CORS
from db import get_connection

app = Flask(__name__)
CORS(app)  # 👈 Habilita CORS para que React pueda consumir el API

@app.route('/api/movimientos', methods=['GET'])
def get_movimientos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, tipo, fecha_hora FROM movimientos")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convertir filas en lista de diccionarios JSON
    movimientos = [
        {
            "id": r["id"],
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "fecha": str(r["fecha_hora"])  # 👈 convertir datetime a string
        }
        for r in rows
    ]
    return jsonify(movimientos)

if __name__ == '__main__':
    app.run(debug=True)
