import json
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:5000'
ENDPOINTS = [
    '/api/session',
    '/api/personas',
    '/api/tarjetas',
    '/api/metrics',
    '/api/reportes/accesos_historial',
    '/api/reportes/tarjetas_historial',
    '/api/movimientos',
    '/api/registros',
    '/api/dispositivos',
    '/api/usuarios',
    '/api/roles',
    '/api/permisos',
    '/api/bitacora'
]

def fetch(path):
    url = BASE + path
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            status = r.getcode()
            text = r.read().decode('utf-8')
            try:
                data = json.loads(text)
            except Exception:
                data = text
            return status, data
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
        except Exception:
            body = ''
        return e.code, body
    except Exception as e:
        return None, str(e)


def short(x):
    if isinstance(x, list):
        return f'list(len={len(x)}) sample=' + (json.dumps(x[:3], ensure_ascii=False) if x else '[]')
    if isinstance(x, dict):
        return 'dict keys=' + ','.join(list(x.keys())[:6])
    return repr(x)[:200]

if __name__ == '__main__':
    print('Checking endpoints against', BASE)
    for ep in ENDPOINTS:
        status, data = fetch(ep)
        print('\n--', ep)
        print('status:', status)
        print('result:', short(data))
