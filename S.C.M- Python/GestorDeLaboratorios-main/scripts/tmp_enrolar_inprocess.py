import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from auth import login_api
import json

app = login_api.app

with app.test_client() as c:
    payload = {
        'persona': {'nombre_completo': 'Test Enrol', 'correo': 'testenrol@test.local', 'tipo_sangre': 'O+'},
        'tarjeta': {'uid': 'ENROL_UID_123', 'nombre_completo': 'Test Enrol', 'correo': 'testenrol@test.local'},
        'perfil': {'nombre': 'Estudiante', 'datos': 'Curso X'}
    }
    r = c.post('/api/enrolar', json=payload)
    print('status', r.status_code)
    print(r.get_data(as_text=True))

    # check bitacora
    r2 = c.get('/api/bitacora')
    print('bitacora', r2.status_code)
    try:
        data = json.loads(r2.get_data(as_text=True))
        for row in data[:8]:
            print(row)
    except Exception as e:
        print('err parsing', e)
