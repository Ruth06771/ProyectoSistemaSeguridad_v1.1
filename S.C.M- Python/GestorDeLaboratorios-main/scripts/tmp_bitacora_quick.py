import requests
base='http://127.0.0.1:5000'
try:
    r1 = requests.post(base+'/api/tarjetas', json={'uid':'BIT_QUICK_UID','nombre_completo':'Bit Quick','correo':'quick@test.local'}, timeout=5)
    print('tarjeta POST', r1.status_code, r1.text)
    r2 = requests.get(base+'/api/bitacora', timeout=5)
    print('bitacora status', r2.status_code)
    data = r2.json()
    for row in data[:5]:
        print(row)
except Exception as e:
    print('FAILED', e)
