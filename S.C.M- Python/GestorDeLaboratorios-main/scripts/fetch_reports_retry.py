import time, json, urllib.request
urls = [
 'http://127.0.0.1:5000/api/reportes/tarjetas_historial',
 'http://127.0.0.1:5000/api/reportes/accesos_historial'
]
for attempt in range(8):
    ok = True
    for u in urls:
        try:
            with urllib.request.urlopen(u, timeout=2) as r:
                data = r.read().decode('utf-8')
                js = json.loads(data)
                print(u, '->', type(js), 'len=', (len(js) if isinstance(js, list) else 'obj'))
                if isinstance(js, list):
                    for i, item in enumerate(js[:3]):
                        print('  ', i, item)
        except Exception as e:
            print('attempt', attempt, 'failed for', u, 'err', e)
            ok = False
    if ok:
        break
    time.sleep(1)
print('done')
