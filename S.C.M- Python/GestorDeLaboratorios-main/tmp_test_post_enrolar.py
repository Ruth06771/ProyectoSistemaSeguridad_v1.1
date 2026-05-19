from flask import Flask
import sqlite3
import json
import sys

# ensure project path
sys.path.insert(0, '.')

from modulos.accesos.enrolar_api import enrolar_api

app = Flask(__name__)
app.register_blueprint(enrolar_api)
app.secret_key = 'test_secret'

sample = {
    "persona": {
        "nombre_completo": "Test Persona Ejemplo",
        "documento_identidad": "TP-0001",
        "correo": "test.persona@example.com"
    },
    "tarjeta": {
        "uid": "TESTUID-0001",
        "pin": "12345678",
        "nombre_completo": "Test Persona Ejemplo",
        "correo": "test.persona@example.com"
    },
    "perfil": {
        "perfil_acceso_lab_id": None,
        "nombre": "Perfil Prueba"
    }
}

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['usuario'] = 'tester'
    resp = client.post('/api/enrolar', json=sample)
    print('POST /api/enrolar status:', resp.status_code)
    try:
        print('response:', json.dumps(resp.get_json(), ensure_ascii=False, indent=2))
    except Exception:
        print('response text:', resp.get_data(as_text=True))

# Query the last historial_enrolamiento row
conn = sqlite3.connect('data/dev.sqlite3')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT * FROM historial_enrolamiento ORDER BY id DESC LIMIT 1')
row = cur.fetchone()
if row:
    d = dict(row)
    print('\nÚltima fila en historial_enrolamiento:')
    print(json.dumps(d, ensure_ascii=False, indent=2))
else:
    print('\nNo se encontró ninguna fila en historial_enrolamiento')
cur.close()
conn.close()
