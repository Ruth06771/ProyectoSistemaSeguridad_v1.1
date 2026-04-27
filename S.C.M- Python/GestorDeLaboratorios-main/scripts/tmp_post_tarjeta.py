import requests
base='http://127.0.0.1:5000'
try:
    post = requests.post(base+'/api/tarjetas', json={'uid':'AUTO_UID_12345','nombre_completo':'Prueba API','correo':'api@test.local'}, timeout=5)
    print('POST status', post.status_code, post.text)
    get = requests.get(base+'/api/tarjetas', timeout=5).json()
    print('Total tarjetas after POST:', len(get))
    for t in get[-5:]:
        print(t)
except Exception as e:
    print('FAILED', e)
