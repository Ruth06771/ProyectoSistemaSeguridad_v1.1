from flask import Flask, jsonify, request
from backend_db import get_connection, log_action  # tu archivo con conexión

app = Flask(__name__)

# Listar personas
@app.route('/api/personas', methods=['GET'])
def listar_personas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre_completo, rol FROM personas")
    rows = cur.fetchall()
    result = [dict(row) for row in rows]
    cur.close()
    return jsonify(result)

# Crear persona
@app.route('/api/personas', methods=['POST'])
def crear_persona():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO personas (nombre_completo, rol) VALUES (%s, %s)",
        (data['nombre_completo'], data['rol'])
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    log_action(conn, 'personas', new_id, 'persona', 'crear', 'system', f'Persona {data["nombre_completo"]} creada')
    return jsonify({'id': new_id})

# Actualizar persona
@app.route('/api/personas/<int:id>', methods=['PUT'])
def actualizar_persona(id):
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE personas SET nombre_completo=%s, rol=%s WHERE id=%s",
        (data['nombre_completo'], data['rol'], id)
    )
    conn.commit()
    cur.close()
    log_action(conn, 'personas', id, 'persona', 'actualizar', 'system', f'Persona {data["nombre_completo"]} actualizada')
    return jsonify({'status': 'ok'})

# Eliminar persona
@app.route('/api/personas/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM personas WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    log_action(conn, 'personas', id, 'persona', 'eliminar', 'system', f'Persona ID {id} eliminada')
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
