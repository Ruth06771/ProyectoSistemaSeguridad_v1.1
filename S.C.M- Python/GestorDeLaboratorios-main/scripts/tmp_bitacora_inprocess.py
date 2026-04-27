import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from auth import login_api
import json

app = login_api.app

with app.test_client() as c:
    # POST persona
    persona = {'nombre':'InProc','apellido':'Tester','correo':'inproc@test.local','rol':'auxiliar'}
    r1 = c.post('/api/personas', json=persona)
    print('persona POST', r1.status_code, r1.get_data(as_text=True))

    # POST tarjeta
    tarjeta = {'uid':'INPROC_UID','nombre_completo':'In Proc','correo':'inproc@test.local'}
    r2 = c.post('/api/tarjetas', json=tarjeta)
    print('tarjeta POST', r2.status_code, r2.get_data(as_text=True))

    # GET bitacora
    r3 = c.get('/api/bitacora')
    print('bitacora', r3.status_code)
    try:
        data = json.loads(r3.get_data(as_text=True))
        for row in data[:10]:
            print(row)
    except Exception as e:
        print('Failed to parse', e)
