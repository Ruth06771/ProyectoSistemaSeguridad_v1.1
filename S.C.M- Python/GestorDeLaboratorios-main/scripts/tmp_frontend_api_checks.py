import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from auth import login_api
app = login_api.app

with app.test_client() as c:
    print('GET /api/personas')
    r = c.get('/api/personas')
    print(r.status_code, r.get_data(as_text=True)[:200])

    print('POST /api/tarjetas (test)')
    r2 = c.post('/api/tarjetas', json={'uid':'TSK_UID_X','nombre_completo':'TSK Test','correo':'tsk@test.local'})
    print(r2.status_code, r2.get_data(as_text=True))

    print('POST /api/personas (test)')
    r3 = c.post('/api/personas', json={'nombre_completo':'TSK Person','correo':'tsk@test.local','tipo_sangre':'A+'})
    print(r3.status_code, r3.get_data(as_text=True))

    print('GET /api/bitacora')
    r4 = c.get('/api/bitacora')
    print(r4.status_code)
    try:
        data = json.loads(r4.get_data(as_text=True))
        print('bitacora rows:', len(data))
    except Exception as e:
        print('err', e)
