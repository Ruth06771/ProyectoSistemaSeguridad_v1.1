import urllib.request, json
for u in ['http://127.0.0.1:5000/api/movimientos', 'http://127.0.0.1:5000/api/registros']:
    try:
        with urllib.request.urlopen(u, timeout=3) as r:
            js = json.loads(r.read().decode('utf-8'))
            print(u, '->', type(js), 'len=', len(js) if isinstance(js, list) else 'obj')
            if isinstance(js, list):
                for it in js[:5]: print('   ', it)
    except Exception as e:
        print(u, 'ERR', e)
