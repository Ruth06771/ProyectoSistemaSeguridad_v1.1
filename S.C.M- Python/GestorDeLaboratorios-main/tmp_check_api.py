import urllib.request
import urllib.error
url = 'http://127.0.0.1:5000/api/reportes/tarjetas_historial'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        print('STATUS', r.status)
        body = r.read().decode('utf-8')
        print(body[:2000])
except urllib.error.HTTPError as e:
    print('HTTPError', e.code)
    try:
        print(e.read().decode('utf-8'))
    except Exception as e2:
        print('read error', e2)
except Exception as e:
    print('ERROR', type(e).__name__, e)
