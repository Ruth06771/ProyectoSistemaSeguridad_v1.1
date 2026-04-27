from flask import Flask, jsonify
from flask_cors import CORS
from db_config import get_connection  # tu archivo que compartiste

app = Flask(__name__)
CORS(app)

@app.route("/api/registros", methods=["GET"])
def obtener_registros():
    conn = get_connection()
    cur = conn.cursor()
    try:
        # SQLite usa ? y MySQL usa %s; get_connection ya da un cursor compatible
        cur.execute("SELECT id, nombre_completo AS nombre, uid FROM tarjetas")
        filas = cur.fetchall()
        
        registros = []
        for fila in filas:
            # fila puede ser dict (MySQL) o sqlite3.Row
            id_ = fila['id'] if 'id' in fila.keys() else fila[0]
            nombre = fila['nombre'] if 'nombre' in fila.keys() else fila[1]
            metodo = "RFID"  # Solo RFID por ahora, si quieres PIN puedes adaptar
            registros.append({
                "id": id_,
                "nombre": nombre,
                "metodo": metodo
            })
        return jsonify(registros)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
